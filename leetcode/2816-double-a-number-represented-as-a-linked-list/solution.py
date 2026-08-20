# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def doubleIt(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev = None
        curr = head
        while curr:
            nxt = curr.next
            curr.next = prev
            prev=curr
            curr=nxt

        new_head = ListNode(0)
        temp = new_head
        carry = 0
        while prev:
            new_val = prev.val*2+carry
            carry = new_val//10
            new_val = new_val%10
            temp.next = ListNode(new_val)
            temp=temp.next
            prev=prev.next
        if carry>0:
            temp.next = ListNode(carry)
        prev = None
        curr = new_head.next
        while curr:
            nxt = curr.next
            curr.next = prev
            prev=curr
            curr=nxt
        return prev