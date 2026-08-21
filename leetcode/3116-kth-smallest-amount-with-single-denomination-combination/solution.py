from typing import List
from math import gcd

class Solution:
    def findKthSmallest(self, coins: List[int], k: int) -> int:

        coins.sort()
        valid = []

        for coin in coins:
            if all(coin % prev != 0 for prev in valid):
                valid.append(coin)

        coins = valid
        n = len(coins)

        def lcm(a, b):
            return a // gcd(a, b) * b

        def count(x):
            total = 0

            for mask in range(1, 1 << n):
                subset_lcm = 1
                bits = 0
                possible = True

                for i in range(n):
                    if mask & (1 << i):
                        bits += 1
                        subset_lcm = lcm(subset_lcm, coins[i])

                        if subset_lcm > x:
                            possible = False
                            break

                if not possible:
                    continue

                multiples = x // subset_lcm

                if bits % 2 == 1:
                    total += multiples
                else:
                    total -= multiples

            return total

        left = 1
        right = min(coins) * k

        while left < right:
            mid = (left + right) // 2

            if count(mid) >= k:
                right = mid
            else:
                left = mid + 1

        return left