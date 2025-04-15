from tpot import TPOTClassifier
import pickle
import numpy as np

from sklearn.model_selection import train_test_split

pfhxs = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,1,0,0,1,0,1,1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0]], dtype=int)

with open("./classification_tables.pkl", 'rb') as fp:
    datasets = pickle.load(fp)

data = datasets[0]['data']

X = data.iloc[:,:-1].to_numpy(dtype=int)
y = data.iloc[:,-1].to_numpy(dtype=int)

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7)

tpot = TPOTClassifier(generations=20, population_size=20, n_jobs=8, verbosity=2, scoring='balanced_accuracy')
tpot.fit(X_train, y_train)

print(tpot.score(X_test, y_test))

output_fname = f"pipeline_{datasets[0]['assay']}.py"
tpot.export(output_fname)

print("## EXPORTED FILE: ##")
with open(output_fname, 'r') as fp:
    print(fp.read())
print("## END EXPORTED FILE ##")

print("## PFHXS PREDICTED PROBABILITY:")
print(tpot.predict_proba(pfhxs))
print("## PFHXS PREDICTED CLASS:")
print(tpot.predict(pfhxs))