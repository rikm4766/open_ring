# train_and_export_c.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import m2cgen as m2c


df = pd.read_csv("data.csv")
X = df[["f1", "f2", "f3", "f4"]].values
y = df["label"].values


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)


y_pred = rf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
joblib.dump(rf, "rf_model.joblib")
print("Saved sklearn model to rf_model.joblib")

# --------------------------------------------------------------#
# model to c code
c_code = m2c.export_to_c(rf, function_name="score_rf")

with open("rf_model.c", "w") as f:
    f.write(c_code)

print("Wrote rf_model.c (C implementation of the RF model)")
