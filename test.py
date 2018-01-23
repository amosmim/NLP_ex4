import eval, extract

if __name__ == '__main__':
    #FeatureBuilder.main('Corpus.TRAIN.txt' ,'train.csv' ,'TRAIN.annotations' ,'model.txt' ,'grafh.png')
    extract.main('Corpus.DEV.txt')
    #extract.main('Corpus.TRAIN.txt')
    eval.main('DEV.annotations' ,'predict.annotations')
    #eval.main('TRAIN.annotations' ,'predict.annotations')