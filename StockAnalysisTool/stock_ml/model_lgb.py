import lightgbm as lgb

def train_lgb(train_df, feature_cols):
    params = dict(
        objective="binary",
        metric="auc",
        learning_rate=0.05,
        num_leaves=31,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=5,
    )
    lgb_train = lgb.Dataset(train_df[feature_cols], label=train_df["target"])
    booster = lgb.train(params, lgb_train, num_boost_round=300)
    return booster
