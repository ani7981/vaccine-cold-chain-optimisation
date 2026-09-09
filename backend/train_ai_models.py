import json
import os
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error
)
from xgboost import XGBClassifier, XGBRegressor

def main():
    print("==================================================================")
    print("     VAXKAVACH PRODUCTION AI PIPELINE (LEAKAGE-FREE & SHAP)       ")
    print("==================================================================")

    data_path = os.path.join(os.path.dirname(__file__), "..", "input_data.csv")
    if not os.path.exists(data_path):
        data_path = "input_data.csv"

    print(f"Loading raw IoT telemetry from: {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} raw records across {df['batch_id'].nunique()} batches.")

    # 1. Standardize Timestamps
    clean_date = df['date'].astype(str).str.replace(r'(\d{1,2})\.(\d{2})$', r'\1:\2', regex=True).str.replace('-', '/')
    df['datetime'] = pd.to_datetime(clean_date, format='mixed')

    # 2. Dual-Probe Redundancy Aggregation
    print("\nAggregating dual-probe redundant IoT loggers...")
    grouped = df.groupby(['batch_id', 'datetime']).agg(
        temp_p1=('thermal_shipper_temp_reading', 'first'),
        temp_p2=('thermal_shipper_temp_reading', 'last'),
        room_temp=('room_temp_reading', 'mean'),
        room_humidity=('room_humidity_reading', 'mean'),
        current_hop=('current_hop', lambda s: 'discarded' if any('discarded' in str(x).lower() for x in s) else s.iloc[0]),
        external_storage=('external_storage', lambda s: 'discarded' if any('discarded' in str(x).lower() for x in s) else s.iloc[0]),
        item_expiry_hours=('item_expiry_hours', 'min'),
        out_of_bound_temperature_hours=('out_of_bound_temperature_hours', 'max')
    ).reset_index().sort_values(['batch_id', 'datetime']).reset_index(drop=True)

    grouped['temp_mean'] = (grouped['temp_p1'] + grouped['temp_p2']) / 2.0
    grouped['probe_discrepancy'] = (grouped['temp_p1'] - grouped['temp_p2']).abs()
    print(f"Aggregated into {len(grouped):,} hourly consensus records across {grouped['batch_id'].nunique()} batches.")

    # 3. Formulate Predictive Lookahead Target (Zero Target Leakage)
    print("\nConstructing forward predictive risk horizon (4-hour lookahead)...")
    feature_dfs = []
    for batch_id, g in grouped.groupby('batch_id'):
        g = g.copy().sort_values('datetime').reset_index(drop=True)
        temp = g['temp_mean']
        room = g['room_temp']

        # Pure thermodynamic & kinetic features (no leakage, no absolute time counters)
        g['thermal_gradient'] = room - temp
        g['temp_delta_1h'] = temp.diff(1).fillna(0.0)
        g['temp_delta_3h'] = temp.diff(3).fillna(0.0)
        g['temp_accel'] = g['temp_delta_1h'].diff(1).fillna(0.0)
        g['temp_rolling_mean_3h'] = temp.rolling(3, min_periods=1).mean()
        g['temp_rolling_std_3h'] = temp.rolling(3, min_periods=1).std().fillna(0.0)
        g['is_frozen_regime'] = (temp < -30.0).astype(float)

        # Ground truth failure event
        is_failed = (
            g['current_hop'].str.contains('discarded', case=False) |
            g['external_storage'].str.contains('discarded', case=False) |
            (g['out_of_bound_temperature_hours'] >= 5) |
            (g['item_expiry_hours'] <= 0)
        )
        # Forward lookahead: failure occurring within [t, t + 4h]
        g['risk_next_4h'] = is_failed.iloc[::-1].rolling(5, min_periods=1).max().iloc[::-1].astype(int)

        # Multi-horizon delta regression targets (physics-informed residual forecasting)
        g['target_delta_1h'] = temp.shift(-1) - temp
        g['target_delta_2h'] = temp.shift(-2) - temp
        g['target_delta_4h'] = temp.shift(-4) - temp

        feature_dfs.append(g)

    df_dataset = pd.concat(feature_dfs, ignore_index=True)

    feature_cols = [
        'temp_mean',
        'probe_discrepancy',
        'room_temp',
        'room_humidity',
        'thermal_gradient',
        'temp_delta_1h',
        'temp_delta_3h',
        'temp_accel',
        'temp_rolling_mean_3h',
        'temp_rolling_std_3h',
        'is_frozen_regime'
    ]

    print(f"Physical Feature set ({len(feature_cols)} features): {feature_cols}")
    print(f"Risk class distribution: {dict(df_dataset['risk_next_4h'].value_counts())}")

    # 4. Chronological Out-of-Sample Batch Split
    train_batches = [f'batch{i:03d}' for i in range(1, 21)]
    test_batches = [f'batch{i:03d}' for i in range(21, 31)]

    train_mask = df_dataset['batch_id'].isin(train_batches)
    test_mask = df_dataset['batch_id'].isin(test_batches)

    X_train = df_dataset.loc[train_mask, feature_cols]
    y_train = df_dataset.loc[train_mask, 'risk_next_4h']
    X_test = df_dataset.loc[test_mask, feature_cols]
    y_test = df_dataset.loc[test_mask, 'risk_next_4h']

    print(f"\nChronological Split: {len(X_train):,} train records ({len(train_batches)} batches), "
          f"{len(X_test):,} test records ({len(test_batches)} unseen holdout batches).")

    # ----------------------------------------------------
    # MODEL 1: FORWARD SPOILAGE / EXCURSION RISK CLASSIFIER
    # ----------------------------------------------------
    print("\n--- Training Model 1: XGBoost Forward Excursion Risk Classifier ---")
    clf = XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric='logloss'
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    cls_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred))
    }

    print("Classifier Holdout Evaluation on Chronologically Future Batches:")
    for k, v in cls_metrics.items():
        print(f"  • {k.upper()}: {v:.4f}")

    # SHAP TreeExplainer
    print("\nInitializing SHAP TreeExplainer for instance-level local interpretability...")
    explainer = shap.TreeExplainer(clf)
    sample_background = X_train.sample(min(200, len(X_train)), random_state=42)
    shap_sample = explainer(sample_background)
    mean_abs_shap = np.abs(shap_sample.values).mean(axis=0)
    shap_rankings = sorted(
        [{"feature": col, "mean_abs_shap": float(score)} for col, score in zip(feature_cols, mean_abs_shap)],
        key=lambda x: x["mean_abs_shap"],
        reverse=True
    )
    print("Top Feature Drivers by Mean |SHAP| Value:")
    for item in shap_rankings[:5]:
        print(f"  • {item['feature']}: {item['mean_abs_shap']:.4f}")

    # ----------------------------------------------------
    # MODEL 2: MULTI-HORIZON TEMPERATURE FORECASTERS (+1h, +2h, +4h)
    # ----------------------------------------------------
    print("\n--- Training Model 2: Multi-Horizon Temperature Forecasters ---")
    reg_models = {}
    reg_metrics = {}

    for horizon in [1, 2, 4]:
        target_col = f'target_delta_{horizon}h'
        valid_tr = train_mask & df_dataset[target_col].notnull()
        valid_te = test_mask & df_dataset[target_col].notnull()

        X_tr_reg = df_dataset.loc[valid_tr, feature_cols]
        y_tr_reg = df_dataset.loc[valid_tr, target_col]
        X_te_reg = df_dataset.loc[valid_te, feature_cols]
        y_te_reg = df_dataset.loc[valid_te, target_col]

        reg = XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.85,
            random_state=42
        )
        reg.fit(X_tr_reg, y_tr_reg)
        y_pr_reg = reg.predict(X_te_reg)

        mae = float(mean_absolute_error(y_te_reg, y_pr_reg))
        rmse = float(np.sqrt(mean_squared_error(y_te_reg, y_pr_reg)))
        reg_metrics[f"ahead_{horizon}h"] = {"mae": round(mae, 3), "rmse": round(rmse, 3)}
        reg_models[f"horizon_{horizon}h"] = reg

        print(f"Forecast Horizon +{horizon}h (Holdout Batches): MAE = {mae:.3f}°C, RMSE = {rmse:.3f}°C")

    # ----------------------------------------------------
    # PERSIST MODEL ARTIFACTS AND METADATA
    # ----------------------------------------------------
    out_dir = os.path.join(os.path.dirname(__file__), "app", "services", "ai", "models")
    os.makedirs(out_dir, exist_ok=True)

    cls_path = os.path.join(out_dir, "xgb_spoilage_classifier.joblib")
    reg_path = os.path.join(out_dir, "xgb_temp_forecaster.joblib")
    explainer_path = os.path.join(out_dir, "shap_explainer.joblib")
    meta_path = os.path.join(out_dir, "model_metadata.json")

    joblib.dump(clf, cls_path)
    joblib.dump(reg_models, reg_path)
    joblib.dump(explainer, explainer_path)

    metadata = {
        "version": "2.0.0-leakage-free-production",
        "formulation": "Dual-Probe Consensus + 4h Forward Lookahead Risk + TreeExplainer SHAP",
        "dataset_records_raw": len(df),
        "dataset_hourly_consensus": len(df_dataset),
        "features": feature_cols,
        "chronological_split": {
            "train_batches": train_batches,
            "test_batches": test_batches
        },
        "classifier_metrics": cls_metrics,
        "forecaster_metrics": reg_metrics,
        "shap_feature_importance": shap_rankings
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nAll models and SHAP explainer successfully persisted to: {out_dir}")
    print("AI Training Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()
