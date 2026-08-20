class Solution:
    def totalSteps(self, nums: List[int]) -> int:
        stack = []
        ans = 0

        for num in nums:
            steps = 0

            while stack and num >= stack[-1][0]:
                steps = max(steps, stack.pop()[1])

            if stack:
                steps += 1

            ans = max(ans, steps)
            stack.append((num, steps))

        return ans