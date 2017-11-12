from pyparsing import *
from math import *
from operator import *
from functools import reduce
from pprint import *

############################################################################
# load: receive an arff filename and create the dicionaries attr and data  #
#                                                                          #
# Example of output:                                                       #
#                                                                          #
# attr = {0: ('outlook',     ('sunny', 'overcast', 'rainy')),              #
#         1: ('temperature', 'numeric'),                                   #
#         2: ('humidity',    'numeric'),                                   #
#         3: ('windy',       ('true', 'false')),                           #
#         4: ('play',        ('yes', 'no'))}                               #
#                                                                          #
# data = { 0: ('sunny',    85.0, 85.0, 'false', 'no' ),                    #
#          1: ('sunny',    80.0, 90.0, 'true',  'no' ),                    #
#          2: ('overcast', 83.0, 86.0, 'false', 'yes'),                    #
#          3: ('rainy',    70.0, 96.0, 'false', 'yes'),                    #
#          4: ('rainy',    68.0, 80.0, 'false', 'yes'),                    #
#          5: ('rainy',    65.0, 70.0, 'true',  'no' ),                    #
#          6: ('overcast', 64.0, 65.0, 'true',  'yes'),                    #
#          7: ('sunny',    72.0, 95.0, 'false', 'no' ),                    #
#          8: ('sunny',    69.0, 70.0, 'false', 'yes'),                    #
#          9: ('rainy',    75.0, 80.0, 'false', 'yes'),                    #
#         10: ('sunny',    75.0, 70.0, 'true',  'yes'),                    #
#         11: ('overcast', 72.0, 90.0, 'true',  'yes'),                    #
#         12: ('overcast', 81.0, 75.0, 'false', 'yes'),                    #
#         13: ('rainy',    71.0, 91.0, 'true',  'no' )}                    #
############################################################################

def load(arff):
    
    # Grammar for the arff format
    
    comment    = '%' + restOfLine
    identifier = Combine(Word(alphas,exact=1) + Optional(Word(alphanums+'_')))
    relation   = Group(Keyword('@relation') + identifier)
    nominal    = Suppress('{') + Group(delimitedList(identifier))  + Suppress('}')
    domain     = (Keyword('numeric') | nominal)
    attribute  = Group(Suppress(Keyword('@attribute')) + identifier('name') + domain('domain'))
    example    = Group(delimitedList(Word(alphanums)))
    arff_fmt   = ( Suppress(relation)
                   + OneOrMore(attribute)('attributes')
                   + Keyword('@data')
                   + OneOrMore(example)('examples') ).ignore(comment)

    # Parse input file and obtain result
    
    with open(arff) as file: text = file.read()
    result = list(arff_fmt.parseString(text))
    middle = result.index('@data')
      
    # create the attribute dictionary from the first part of the result
    
    attr = {} # attribute dictionary
    
    for (i,v) in enumerate(result[:middle]):
        attr[i] = (v[0],v[1] if v[1]=='numeric' else tuple(v[1]))

    # create the data dictionary from the second part of the result

    data = {} # data dictionary (must be consisted)

    for (i,w) in enumerate(result[middle+1:]):
        data[i] = tuple( (float(v) if attr[i][1]=='numeric' else v) for (i,v) in enumerate(w) )

    print('\nattr =') ; pprint(attr)
    print('\ndata =') ; pprint(data)

    return (attr, data)

############################################################################
# digest: receive the dictionaries att and data and create the dicionaries #
#         dap (discrete attribute probability) and                         #
#         cap (continuous  attribute probability)                          #
#                                                                          #
# Example of output:                                                       #
#                                                                          #
# dap = {('outlook', 'overcast', 'yes'): 0.44,                             #
#        ('outlook', 'rainy',    'no' ): 0.40,                             #
#        ('outlook', 'rainy',    'yes'): 0.33,                             #
#        ('outlook', 'sunny',    'no' ): 0.60,                             #
#        ('outlook', 'sunny',    'yes'): 0.22,                             #
#        ('play',                'no' ): 0.36,                             #
#        ('play',                'yes'): 0.64,                             #
#        ('windy',   'false',    'no' ): 0.40,                             #
#        ('windy',   'false',    'yes'): 0.67,                             #
#        ('windy',   'true',     'no' ): 0.60,                             #
#        ('windy',   'true',     'yes'): 0.33}                             #
#                                                                          #
# cap = {('humidity',    'no' ): (86.2,  9.7),                             #
#        ('humidity',    'yes'): (79.1, 10.2),                             #
#        ('temperature', 'no' ): (74.6,  7.9),                             #
#        ('temperature', 'yes'): (73.0,  6.2)}                             #
############################################################################

def digest(attr,data):
    dap = {}                   # discrete attribute probability dictionary
    cap = {}                   # continuous attribute probability dictionary
    can = attr[len(attr)-1][0] # class attribute name
    
    # update accumulators for discrete and continuous attributes
    
    for i, example in enumerate(data.values()):
        cav = example[-1]      # class attribute value
        dap[(can,cav)] = dap.get((can,cav),0) + 1
        for j, field in enumerate(example[:-1]):
            if attr[j][1] == 'numeric':
                cap[(attr[j][0],cav)] = cap.get((attr[j][0],cav),0) + field
            else:
                dap[(attr[j][0],field,cav)] = dap.get((attr[j][0],field,cav),0) + 1

    # update accumulators with means
    
    for key in dap:
        cav = key[-1]
        if key[0] != can:
            dap[key] /= dap.get((can,cav),1) # 1, if key does not exist
    
    for key in cap:
        cap[key] /= dap.get((can,key[-1]),1) # 1, if key does not exist

    
    # compute the sum of squared differences for continuous attributes
    
    nat = [(i,key[0]) for i, key in attr.items() if key[1]=='numeric'] # numeric attributes

    ssd = {}

    for example in data.values():
        for i, field in nat:
            cav = example[-1]
            ssd[(field,cav)] = ssd.get((field,cav),0) + (example[i]-cap.get((field,cav),0))**2

    # update values of keys for continuous attributes with standard deviation

    for key in ssd:
        cav = key[-1]
        std = (ssd[key]/(dap[(can,cav)]-1))**0.5
        cap[key] = (cap[key],std)

    # update mean of class attribute counters

    for key in dap:
        if len(key) == 2:
            dap[key] /= len(data)

    print('\ndap =')  ; pprint(dap)
    print('\ncap =')  ; pprint(cap)

    return (dap, cap)


############################################################################
# Gaussian probability distribution function                               #
############################################################################

def gauss(x,m,s): return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((x-m)/s)**2)


############################################################################
# Attribute-value-class probability function                               #
############################################################################

def prob(attr,dap,cap,attribute_column,attribute_value,class_value):
    (attribute_name, attribute_domain) = attr[attribute_column]
    if attribute_domain == 'numeric':
        (mean, standard_deviation) = cap[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        # return 1 if key does not exist (laplacian correction?)
        return dap.get((attribute_name,attribute_value,class_value),1) 


############################################################################
# Bayesian classification function                                         #
############################################################################

def classification(attr,dap,cap,instance):
    class_attribute_column = len(attr)-1
    class_attribute_name   = attr[class_attribute_column][0]
    class_attribute_domain = attr[class_attribute_column][1]

    # compute likelihoods
    
    likelihoods = [ [prob(attr,dap,cap,i,instance[i],class_value)
                     for i in range(len(instance))]
                    + [dap[(class_attribute_name,class_value)]]
                    for class_value in class_attribute_domain ]
    likelihoods = [reduce(mul,likelihood,1) for likelihood in likelihoods]

    # compute probabilities
    
    denominator = sum(likelihoods)
    probs = list(zip([likelihood/denominator for likelihood in likelihoods],
                     class_attribute_domain))
    
    # the next two line are only for debug purpose

    print('\nResult for %s:' % instance)

    for (probability,class_value) in probs:
        print('prob[%s] = %.1f%%' % (class_value,probability*100))
        
    return max(probs)[1]

############################################################################
# Code for test, based on the example given in page 96 of the book         #
############################################################################
   

attr, data = load('golf-mixed.arff')
dap, cap = digest(attr,data)

instance1 = ['sunny',66,90,'true']
pcv = classification(attr,dap,cap,instance1)
print('Predicted class value: "%s"' % pcv)

instance2 = ['overcast',66,50,'true']
pcv = classification(attr,dap,cap,instance2)
print('Predicted class value: "%s"' % pcv)



    


