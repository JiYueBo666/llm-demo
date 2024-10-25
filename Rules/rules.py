from abc import ABC, abstractmethod
import json
import os,sys
from collections import defaultdict
sys.path.append('./')
from llm.utils import time_logger,get_green_logger

logger=get_green_logger()

class Condition():
    def __init__(self) -> None:
        self.condition_idx:int=0
        self.key_words:str=''


class BaseRules(ABC):
    def __init__(self) -> None:
        
        pass

    @abstractmethod
    def check_rules(self):
        pass


class IntentRules(BaseRules): 
    def __init__(self) -> None:
        '''
        意图识别的模块。rule based。
        限定某些意图的功能，避免误触大模型
        '''
        super().__init__()
        self.synonym_dict = {}
        self.intent_dict=defaultdict(str)
        self.load_synonym_dict()
        self.load_intent_dict()

    def get_item(self):
        return self.intent_dict

    @time_logger
    def load_synonym_dict(self):
        '''
        触发意图的同义词词典。
        '''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        synonym_file = os.path.join(current_dir, 'synonym.json')
        logger.info(f'loading synonym dict from {synonym_file}')
        with open(synonym_file, 'r', encoding='utf-8') as f:
            self.synonym_dict = json.load(f)
        logger.info('synonym dict loaded')

    def load_intent_dict(self):
        for key in self.synonym_dict.keys():
            if key not in self.intent_dict.keys():
                self.intent_dict[key]=len(self.intent_dict)

    def __call__(self, query: str) -> Condition:
        return self.check_rules(query)


    def check_rules(self, query: str) -> Condition:
        '''
        #检查意图，返回一个condition类对象。该对象拥有意图关键词和意图索引属性。
        '''
        condition = Condition()
        for key, synonyms in self.synonym_dict.items():
            if any(synonym in query for synonym in synonyms):
                condition.key_words = key
                condition.condition_idx=self.intent_dict[key] 
                return condition 
        return None




if __name__ == "__main__":
    rules = IntentRules()
    result = rules('帮我查下三国演义的陈登')
