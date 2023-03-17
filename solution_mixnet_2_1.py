from os import getenv
from dotenv import load_dotenv
from requests.api import get
from mixnet_client import MixnetClient, load_pem_file
from simulator import MixnetSimulator
import requests

# constants definitions
NUMBER_ITERATIONS = 30 
THRESHOLD_3 = 5
MAX_THRESHOLD = 7

class Analyzer:
    def __init__(self) -> None:
        self.client = MixnetClient()
        self.total_messages = 0
        self.messages_delivered = 0
        self.messages_pipeline = 0
        requests.packages.urllib3.disable_warnings()

    def count_message_delivered(self, message):
        response = requests.get('https://pets.kmoragas.com/log/3-wa92tywpZb17N86jdOctpTWw6XwHGkyaVwPjWDGI3tA=/exit.txt', verify=False)

        return response.content.decode().count(message)


    def clear_pipeline(self):
        print('** Emptying the pipeline of the mixnet 2 to start the analysis **')
        print('=> processing...')
        batch=6
        recipient = 'analyzer'
        message = 'emptying the pipeline'
        encrypted_message = self.client.encrypt_message(('%s, %s' % (recipient, message)).encode())

        flag = True
        while flag:
            for j in range(batch):
                self.client.send(encrypted_message)
                self.total_messages += 1
            batch=7

            self.messages_delivered = self.count_message_delivered(message) 
            self.messages_pipeline = (self.total_messages) - (self.messages_delivered)
            flag = self.messages_pipeline != 0

        self.total_messages = 0
        self.messages_delivered = 0
        self.messages_pipeline = 0

    def analize_mixnet(self):
        self.clear_pipeline()
        print('** Analyzing the mixnet 2 **')
        print('=> processing...')
        recipient = 'alvaro'
        message = 'This is a test message for Alvaro!'
        encrypted_message = self.client.encrypt_message(('%s, %s' % (recipient, message)).encode())
        batch=7
        candidate_thresholds = []
        list_messages_pipeline = []

        for i in range(NUMBER_ITERATIONS):
            for j in range(batch):
                self.client.send(encrypted_message)
                self.total_messages += 1

            self.messages_delivered = self.count_message_delivered(message) 
            self.messages_pipeline = (self.total_messages) - (self.messages_delivered)
            
            list_messages_pipeline.append(self.messages_pipeline)
            print({ 'totalMessages': self.total_messages, 'deliveredMessages': self.messages_delivered, 'pipelineMessages': self.messages_pipeline })
            if self.messages_pipeline == 0:
                divisors = self.get_divisors(self.total_messages)
                if len(candidate_thresholds) == 0:
                    candidate_thresholds = divisors 
                else:
                    candidate_thresholds = [candidate for candidate in candidate_thresholds if candidate in divisors]
        print('** Candidate list of thresholds for the mixnet 2 **')
        print('=> List: ', candidate_thresholds)
        return candidate_thresholds, list_messages_pipeline
                
    def get_divisors(self, number):
        divisors = []
        for divisor in range(1, MAX_THRESHOLD + 1):
            if (number % divisor) == 0:
                divisors.append(divisor)
        return divisors

if __name__ == '__main__':
    analizer = Analyzer()
    candidate_thresholds, list_messages_pipeline = analizer.analize_mixnet()

    print('** Running mixnet simulator to find the thresholds of the mixes **')
    for i in range(len(candidate_thresholds)):
        simulator = MixnetSimulator(candidate_thresholds[i], MAX_THRESHOLD, THRESHOLD_3)
        simulator_candidate_thresholds = simulator.start(NUMBER_ITERATIONS)

        if simulator_candidate_thresholds == list_messages_pipeline:
            print('** THRESHOLD_1 = %s, THRESHOLD_2 = %s, THRESHOLD_3 = %s **' % (candidate_thresholds[i], MAX_THRESHOLD, THRESHOLD_3))
            break
        else:
            simulator = MixnetSimulator(MAX_THRESHOLD, candidate_thresholds[i], THRESHOLD_3)
            simulator_candidate_thresholds = simulator.start(NUMBER_ITERATIONS)
            if simulator_candidate_thresholds == list_messages_pipeline:
                print('** THRESHOLD_1 = %s, THRESHOLD_2 = %s, THRESHOLD_3 = %s **' % (MAX_THRESHOLD, candidate_thresholds[i], THRESHOLD_3))
                break
