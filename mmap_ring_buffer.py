import mmap
import struct
import os

class MMapRingBuffer:
    def __init__(self, size: int = 1024):
        self.size = size
        # Format string: 
        # 'I' = unsigned int (4 bytes) for message type/id
        # 'q' = long long (8 bytes) for integer value/timestamp
        self.struct_format = 'Iq'
        self.msg_size = struct.calcsize(self.struct_format) # Total bytes per message (12 bytes)
        
        # Create an anonymous memory-mapped file buffer (shared in memory)
        self.mmap_file = mmap.mmap(-1, size)
        
        # Head (write pointer) and Tail (read pointer) indices
        self.head = 0
        self.tail = 0

    def write(self, msg_id: int, value: int) -> bool:
        """Packs integers using struct and writes to the mmap buffer."""
        packed_data = struct.pack(self.struct_format, msg_id, value)
        
        # Check for buffer overflow
        next_head = (self.head + self.msg_size) % self.size
        if next_head == self.tail:
            return False  # Buffer full
            
        # Move pointer and write data into memory-mapped region
        self.mmap_file.seek(self.head)
        self.mmap_file.write(packed_data)
        self.head = next_head
        return True

    def read(self):
        """Reads from mmap buffer and unpacks bytes back into integers."""
        if self.head == self.tail:
            return None  # Buffer empty
            
        self.mmap_file.seek(self.tail)
        packed_data = self.mmap_file.read(self.msg_size)
        
        # Unpack binary data back to original integers
        msg_id, value = struct.unpack(self.struct_format, packed_data)
        
        self.tail = (self.tail + self.msg_size) % self.size
        return {"msg_id": msg_id, "value": value}

    def close(self):
        self.mmap_file.close()

# --- Example Usage ---
if __name__ == "__main__":
    # Initialize ring buffer with 1KB size
    ring_buffer = MMapRingBuffer(size=1024)

    # Write integer data (e.g., Order ID and Price/Quantity)
    print("Writing messages to mmap ring buffer...")
    ring_buffer.write(msg_id=101, value=15000)
    ring_buffer.write(msg_id=102, value=15025)

    # Read/Unpack the data back
    print("\nReading messages from mmap ring buffer:")
    while True:
        msg = ring_buffer.read()
        if msg is None:
            break
        print(f"Unpacked -> Message ID: {msg['msg_id']}, Value: {msg['value']}")

    ring_buffer.close()
