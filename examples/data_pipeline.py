"""
Example of using reliabilipy for a resilient data processing pipeline.
Shows state management for recovery and metrics collection.
"""
from reliabilipy import StateManager, observe, MetricsCollector
import json
from typing import List, Dict

metrics = MetricsCollector(namespace="data_pipeline")

class DataPipeline:
    def __init__(self, input_data: List[Dict]):
        self.state = StateManager(
            backend='file',
            namespace='data_pipeline',
            file_path='.pipeline_state.json'
        )
        self.input_data = input_data
        
    @observe(name="process_batch", metrics=metrics)
    def process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Process a batch of data with automatic metrics collection."""
        return [self._transform_item(item) for item in batch]
    
    def _transform_item(self, item: Dict) -> Dict:
        """Transform a single data item."""
        return {
            "id": item["id"],
            "value": item["value"] * 2,
            "processed": True
        }
    
    def run(self, batch_size: int = 10):
        """Run the pipeline with state recovery."""
        # Get last processed position
        last_position = self.state.get("last_position", 0)
        print(f"Resuming from position: {last_position}")
        
        try:
            for i in range(last_position, len(self.input_data), batch_size):
                batch = self.input_data[i:i + batch_size]
                processed = self.process_batch(batch)
                
                # Store results and update state
                self.state.set("last_position", i + len(batch))
                print(f"Processed batch: {i}-{i + len(batch)}")
                
                # In a real application, you would store processed data
                # self.store_results(processed)
                
        except Exception as e:
            print(f"Error processing batch: {e}")
            print("State saved, can resume from last successful position")
            raise

def main():
    # Example input data
    input_data = [
        {"id": i, "value": i} for i in range(100)
    ]
    
    pipeline = DataPipeline(input_data)
    pipeline.run(batch_size=10)

if __name__ == '__main__':
    main()
