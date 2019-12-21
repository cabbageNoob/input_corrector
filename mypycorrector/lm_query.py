'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-20 13:06:59
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-20 16:31:42
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
        self.process = None

    def _exec(self, txt):
        if self.process is None:
            self.process = subprocess.Popen([self.execute, "-b", self.model], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        self.process.stdin.write(f"{txt} \n".encode(self.encode))
        self.process.stdin.flush()
        return self.process.stdout.readline().decode(self.encode)


    def score(self, sentence):
        '''
        @Descripttion:  Return the log10 probability of a string.
        @param {type} 
        @return: 
        '''   
        score_txt = self._exec(sentence)
        total = 0.
        char_scores = score_txt.split('\t')
        print(char_scores)
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
    
