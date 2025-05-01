"""
Example of using reliabilipy for chaos engineering in a microservice.
Shows how to use failure injection for testing resilience.
"""
from reliabilipy import inject_failure, inject_latency, assert_invariant
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class User:
    id: int
    name: str
    balance: float

class UserService:
    def __init__(self):
        self.users: Dict[int, User] = {}
        
    @inject_failure(rate=0.1, exception=RuntimeError, message="Database connection failed")
    def create_user(self, id: int, name: str) -> User:
        """Create a new user with random failures to test error handling."""
        user = User(id=id, name=name, balance=0.0)
        self.users[id] = user
        return user
    
    @inject_latency(min_delay=0.1, max_delay=0.5)
    def get_user(self, id: int) -> Optional[User]:
        """Get user details with random latency to test timeouts."""
        return self.users.get(id)
    
    def transfer_money(self, from_id: int, to_id: int, amount: float) -> bool:
        """Transfer money between users with invariant checks."""
        from_user = self.get_user(from_id)
        to_user = self.get_user(to_id)
        
        if not from_user or not to_user:
            return False
            
        # Check invariants before transfer
        assert_invariant(
            lambda: from_user.balance >= amount,
            "Insufficient funds"
        )
        
        # Perform transfer
        from_user.balance -= amount
        to_user.balance += amount
        
        # Verify invariants after transfer
        assert_invariant(
            lambda: from_user.balance >= 0,
            "Account balance cannot be negative"
        )
        
        return True

def main():
    # Example usage
    service = UserService()
    
    try:
        # This might randomly fail
        user1 = service.create_user(1, "Alice")
        user2 = service.create_user(2, "Bob")
        print("Created users successfully")
        
        # This will have random latency
        alice = service.get_user(1)
        print(f"Retrieved user: {alice}")
        
        # Test money transfer with invariants
        service.users[1].balance = 100.0
        try:
            success = service.transfer_money(1, 2, 50.0)
            print(f"Transfer {'succeeded' if success else 'failed'}")
            print(f"Alice's balance: {service.users[1].balance}")
            print(f"Bob's balance: {service.users[2].balance}")
        except AssertionError as e:
            print(f"Transfer failed due to invariant violation: {e}")
            
    except RuntimeError as e:
        print(f"Service failed: {e}")

if __name__ == '__main__':
    main()
