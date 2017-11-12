class bayes:
    def __init__(self,filename):
        self.attributes = []
        self.domain = {}
        self.c_attr = None
        self.data = []
        self.frequency = {}
        self.probability = {}
        with open(filename) as file:
            for line in file:
                tokens = [t for t in line.replace('\n','').replace(',',' ').split(' ') if t != '']
                if tokens==[] or tokens[0] in ['%','@relation','@data']: continue
                if tokens[0]=='@attribute':
                    attribute = tokens[1].replace('-','_')
                    values = [v.replace('{','').replace('}','') for v in tokens[2:]]
                    self.attributes.append(attribute)
                    self.domain[attribute]=tuple(values)
                else:
                    self.data.append(tuple(tokens))
            if self.c_attr==None: self.c_attr = self.attributes[-1]

    def frequencies(self, show=False):
        if self.frequency != {}: return
        for c_value in self.domain[self.c_attr]:
            self.frequency[(self.c_attr,c_value)] = 0
            for attribute in self.attributes:
                if attribute != self.c_attr:
                    for value in self.domain[attribute]:
                        self.frequency[(attribute,value,c_value)] = 0
        for example in self.data:
            for (attribute,value) in zip(self.attributes,example):
                if attribute == self.c_attr: event = (attribute,value)
                else: event = (attribute,value,example[-1])
                self.frequency[event] += 1
        if show:
            for event in sorted(self.frequency.keys()):
                print('frequency[%s] = %d' % (event,self.frequency[event]))
            print()

    def probabilities(self, show=False):
        if self.probability != {}: return
        for event in self.frequency.keys():
            if len(event) == 3: self.probability[event] = self.frequency[event]/self.frequency[(self.c_attr,event[-1])]
        total = sum(self.frequency[(self.c_attr,c_value)] for c_value in self.domain[self.c_attr])
        for c_value in self.domain[self.c_attr]:
            self.probability[(self.c_attr,c_value)] = self.frequency[(self.c_attr,c_value)]/total
        if show:
            for event in sorted(self.probability.keys()):
                print('probability[%s] = %.1f' % (event,self.probability[event]))
            print()

    def classification(self,instance,show=False):
        self.frequencies(show)
        self.probabilities(show)
        prob = {}
        for c_value in self.domain[self.c_attr]:
            prob[c_value] = self.probability[(self.c_attr,c_value)]
            for (attribute,value) in zip(self.attributes,instance):
                prob[c_value] *= self.probability[(attribute,value,c_value)]
        total = sum(prob.values())
        for c_value in self.domain[self.c_attr]:
            prob[c_value] = prob[c_value]*100/total
        if show: 
            for c_value in prob.keys():
                print('prob[%s] = %.1f%%' % (c_value,prob[c_value]))
            print()
        return sorted(prob.items(),key = lambda x: x[1], reverse=True)[0][0]


model = bayes('golf.arff')
print(model.classification(['sunny','cool','high','true'],True))

model = bayes('lenses.ts.arff')
print(model.classification(['young','hypermetrope','no','normal']))

input('enter...')

model = bayes('person.arff')
print(model.classification(['morgan','no','brown','short'],True))
