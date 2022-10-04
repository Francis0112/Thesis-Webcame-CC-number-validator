def checkLuhn(cardNo):
        nDigits = len(cardNo)
        nSum = 0
        isSecond = False

        for i in range(nDigits - 1, -1, -1):
            d = ord(cardNo[i]) - ord('0')

            if (isSecond == True):
                d = d * 2

            # We add two digits to handle
            # cases that make two digits after
            # doubling
            nSum += d // 10
            nSum += d % 10

            isSecond = not isSecond

        if (nSum % 10 == 0):
            return True
        else:
            return False
        
        
real_pbcom = "5237362307293793"
generated = "3442591826344259"
int(generated)
if (checkLuhn(generated)):
    print("real credit card")
else:
    print("fake credit card")
    
#4234261826345918
#5991837567594234
#3442591826344259