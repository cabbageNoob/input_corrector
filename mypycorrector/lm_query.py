'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-20 13:06:59
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-20 13:47:11
'''
import subprocess

class KenLMQuery:
    def __init__(self, model, execute, encode="utf-8"):
        """
        model: path to model
        execute: path to query in KenLM
        """
        self.model = model
        self.execute = execute
        self.encode = encode

    def _exec(self, txt):
        try:
            p = subprocess.Popen([self.execute, self.model], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
            out, error = p.communicate(txt.encode(self.encode))
            return "" if out is None else out.decode(self.encode), "" if error is None else error.decode(self.encode)
        except Exception as e:
            print("occur exception")
            print(e)


    def score(self, sentence):
        '''
        @Descripttion:  Return the log10 probability of a string.
        @param {type} 
        @return: 
        '''   
        score_txt = self._exec(sentence+'UNK')[0]
        total = 0.
        char_scores = score_txt.split('\t')
        return sum([float(_.split()[-1]) for _ in char_scores[:-1]])


    def perplexity(self, sentence):
        '''
        @Descripttion:  Compute perplexity of a sentence.
        @param {type} 
        @return: 
        '''    
        words = len((sentence).split()) + 1
        return 10.0 ** (-self.score(sentence) / words)
        
if __name__ == '__main__':
    kenlmquery = KenLMQuery(model=r'C:\Users\cjh\.pycorrector\datasets\zh_giga.no_cna_cmn.prune01244.klm', \
         execute=r'D:\LMModel\pycorrector_git\mypycorrector\kenlm_ngram_query_x64.exe')
    print(kenlmquery.score('北 京 理 工 大 学'))
    print(kenlmquery.perplexity('北 京 理 工 大 学'))
    
