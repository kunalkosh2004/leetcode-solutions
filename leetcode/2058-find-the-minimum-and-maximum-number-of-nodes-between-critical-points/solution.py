# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def nodesBetweenCriticalPoints(self, head: Optional[ListNode]) -> List[int]:
        prev = head
        curr = head.next
        ct=1
        arr = []
        while curr.next:
            nxt = curr.next
            if prev.val<curr.val>nxt.val or prev.val>curr.val<nxt.val:
                arr.append(ct)
            ct+=1
            prev=curr
            curr=curr.next
        if len(arr) < 2:
            return [-1, -1]

        min_diff = min(arr[i] - arr[i - 1] for i in range(1, len(arr)))
        max_diff = arr[-1] - arr[0]

        return [min_diff, max_diff]