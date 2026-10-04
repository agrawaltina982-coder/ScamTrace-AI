import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/sample_cases.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].fillna(""), df["label"], test_size=0.25,
        random_state=42, stratify=df["label"]
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(classification_report(y_test, pred, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, pred))

if __name__ == "__main__":
    main()
