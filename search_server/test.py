import pypinyin
print(pypinyin.lazy_pinyin('中心'))

from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi

hmmparams = DefaultHmmParams()

## 2个候选
result = viterbi(hmm_params=hmmparams, observations=('ping', 'ying'), path_num = 10)
for item in result:
    print(item.score, item.path)