import random
import time
for i in range(100):
    time.sleep(1)
    print("%d epoch %d batch loss: %f" %(i//10, i%10, 100*random.random()))