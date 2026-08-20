# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def splitListToParts(self, head: Optional[ListNode], k: int) -> List[Optional[ListNode]]:
        n = 0
        temp = head
        while temp:
            n+=1
            temp = temp.next
        
        size = n//k
        extra = n%k
        curr = head
        ans = []
        for i in range(k):
            part_head = curr
            part_size = size
            if extra>0:
                part_size+=1
                extra-=1
            for _ in range(part_size-1):
                if curr:
                    curr=curr.next
            if curr:
                nxt = curr.next
                curr.next=None
                curr=nxt
            ans.append(part_head)
        return ans
            