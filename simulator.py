class Mix:
    def __init__(self, batch) -> None:
        self.batch = batch
        self.queue = 0

class MixnetSimulator:
    def __init__(self, threshold_1, threshold_2, threshold_3) -> None:
        print('=> Testing: THRESHOLD_1 = %s, THRESHOLD_2 = %s, THRESHOLD_3 = %s' % (threshold_1, threshold_2, threshold_3))
        self.mix_1 = Mix(threshold_1) 
        self.mix_2 = Mix(threshold_2)
        self.mix_3 = Mix(threshold_3) 
        self.messages_sent = 0
        self.messages_delivered = 0
        self.m_sent = 7
        self.summary = []

    def start(self, n):
        list_messages_pipeline = []
        for i in range(n):
            self.m_sent = 7
            self.messages_sent += self.m_sent

            self.mix_1.queue = self.m_sent + self.mix_1.queue
            self.m_sent = 0
            while self.mix_1.queue >= self.mix_1.batch:
                if (self.mix_1.queue - self.mix_1.batch) >= self.mix_1.batch or (self.mix_1.queue - self.mix_1.batch) >= 0:
                    self.mix_1.queue = self.mix_1.queue - self.mix_1.batch
                    self.m_sent += self.mix_1.batch

            self.mix_2.queue = self.m_sent + self.mix_2.queue
            self.m_sent = 0
            while self.mix_2.queue >= self.mix_2.batch: 
                if (self.mix_2.queue - self.mix_2.batch) >= self.mix_2.batch or (self.mix_2.queue - self.mix_2.batch) >= 0:
                    self.mix_2.queue = self.mix_2.queue - self.mix_2.batch
                    self.m_sent += self.mix_2.batch

            self.mix_3.queue = self.m_sent + self.mix_3.queue
            self.m_sent = 0
            while self.mix_3.queue >= self.mix_3.batch: 
                if (self.mix_3.queue - self.mix_3.batch) >= self.mix_3.batch or (self.mix_3.queue - self.mix_3.batch) >= 0:
                    self.mix_3.queue = self.mix_3.queue - self.mix_3.batch
                    self.m_sent += self.mix_3.batch

            self.messages_delivered += self.m_sent
            self.summary.append({ 'totalMessages': self.messages_sent, 'deliveredMessages': self.messages_delivered, 'pipelineMessages': self.messages_sent - self.messages_delivered })
            list_messages_pipeline.append(self.messages_sent - self.messages_delivered)
        return list_messages_pipeline

    def show_results(self):
        for i in range(len(self.summary)):
            print(self.summary[i])

