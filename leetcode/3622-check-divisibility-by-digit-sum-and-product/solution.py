class Solution:
    def checkDivisibility(self, n: int) -> bool:
        orig = n
        s = 0
        prod = 1
        while n>0:
            digit = n%10
            s+=digit
            prod*=digit
            n//=10
        div = s+prod
        return orig%div==0