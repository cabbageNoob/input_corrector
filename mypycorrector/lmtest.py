import kenlm
model = kenlm.LanguageModel('./data/kenlm/people2014corpus_chars.klm')
score=model.score("我额单鹄寡凫波斯尼亚们要去 天 安 门")
print(score)