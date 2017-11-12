from math import *
from operator import *
from functools import reduce
from pprint import pprint

############################################################################
# Data extracted from the ARFF file corresponding to Table 1.3 of the book #
############################################################################

# Attribute dictionary
# attribute_column : (attribute_name, attribute_domain)

attr_dict = { 0 : ('outlook',    ['sunny','overcast','rainy']),
              1 : ('temperature','numeric'),
              2 : ('humidity',   'numeric'),
              3 : ('windy',      ['true','false']),
              4 : ('play',       ['yes','no']) }

# discrete attribute probability dictionary (without Laplacian correction!)
# (attribute_name, attribute_value, class_value) : probability

dap_dict = { ('outlook', 'sunny',    'yes') : 2/9,
             ('outlook', 'sunny',    'no' ) : 3/5,
             ('outlook', 'overcast', 'yes') : 4/9,
             ('outlook', 'overcast', 'no' ) : 0/5,
             ('outlook', 'rainy',    'yes') : 3/9,
             ('outlook', 'rainy',    'no' ) : 2/5, 
             ('windy',   'false',    'yes') : 6/9,
             ('windy',   'false',    'no' ) : 2/5,
             ('windy',   'true',     'yes') : 3/9,
             ('windy',   'true',     'no' ) : 3/5,
             ('play',    'yes'            ) : 9/14,
             ('play',    'no'             ) : 5/14}

# continuous attribute probability dictionary
# (attribute_name, class_value) : (mean, standard_deviation)

cap_dict = { ('temperature', 'yes') : (73.0,  6.2),
             ('temperature', 'no' ) : (74.6,  7.9),
             ('humidity',    'yes') : (79.1, 10.2),
             ('humidity',    'no' ) : (86.2,  9.7),}

data= [['sunny',    85, 85, 'false', 'no' ],
       ['sunny',    80, 90, 'true',  'no' ],
       ['overcast', 83, 86, 'false', 'yes'],
       ['rainy',    70, 96, 'false', 'yes'],
       ['rainy',    68, 80, 'false', 'yes'],
       ['rainy',    65, 70, 'true',  'no' ],
       ['overcast', 64, 65, 'true',  'yes'],
       ['sunny',    72, 95, 'false', 'no' ],
       ['sunny',    69, 70, 'false', 'yes'],
       ['rainy',    75, 80, 'false', 'yes'],
       ['sunny',    75, 70, 'true',  'yes'],
       ['overcast', 72, 90, 'true',  'yes'],
       ['overcast', 81, 75, 'false', 'yes'],
       ['rainy',    71, 91, 'true',  'no' ]]



counter = {}
#result = {}

for i,linha in enumerate(data):
    c = linha[-1]
    counter[(c,)] = counter.get((c,),0)+1
    for j,coluna in enumerate(linha[:-1]):
        if attr_dict[j][1] == 'numeric':
            counter[(attr_dict[j][0],c)] = counter.get((attr_dict[j][0],c),0) + coluna
        else:
            counter[(attr_dict[j][0],coluna,c)] = counter.get((attr_dict[j][0],coluna,c),0) + 1

 
for k in counter:
    if len(k)>1:
        counter[k] /= counter[(k[-1],)]
        
        
interessa = interessa = [(i,k[0]) for i,k in attr_dict.items() if k[1]=='numeric']
    

dif = {}
for linha in data:
    for c,a in interessa:
	    dif[(a,linha[-1])] = dif.get((a,linha[-1]),0) + (linha[c]-counter[(a,linha[-1])])**2

pprint(dif)
############################################################################
# Gaussian probability distribution function                               #
############################################################################

def gauss(x,m,s): return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((x-m)/s)**2)


############################################################################
# Attribute-value-class probability function                               #
############################################################################

def prob(attribute_column,attribute_value,class_value):
    (attribute_name, attribute_domain) = attr_dict[attribute_column]
    if attribute_domain == 'numeric':
        (mean, standard_deviation) = cap_dict[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        return dap_dict[(attribute_name,attribute_value,class_value)]


############################################################################
# Bayesian classification function                                         #
############################################################################

def classification(instance):
    class_attribute_column = len(attr_dict)-1
    class_attribute_name   = attr_dict[class_attribute_column][0]
    class_attribute_domain = attr_dict[class_attribute_column][1]
    likelihoods = [ [prob(i,instance[i],class_value)
                                for i in range(len(instance))]
                    + [dap_dict[(class_attribute_name,class_value)]]
                    for class_value in class_attribute_domain ]
    # the next line is only for debug purpose
    # print(likelihoods)
    likelihoods = [reduce(mul,likelihood,1) for likelihood in likelihoods]
    # the next line is only for debug purpose
    # print(likelihoods)
    denominator = sum(likelihoods)
    probs = list(zip([likelihood/denominator for likelihood in likelihoods],
                     class_attribute_domain))
    # the next two line are only for debug purpose
    for (probability,class_value) in probs:
        print('prob[%s] = %.1f%%' % (class_value,probability*100))
    return max(probs)[1]

############################################################################
# Code for test, based on the example given in page 96 of the book         #
############################################################################
   
instance = ['sunny',66,90,'true']

#print('Predicted class value: "%s"' % classification(instance))

