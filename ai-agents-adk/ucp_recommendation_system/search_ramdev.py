import sys
import os
import json

# Add project root to path if needed (though usually not if run from root)
sys.path.append(os.getenv("SYS_PATH"))
# Add the specific directory to sys.path
sys.path.append(os.getenv("SYS_PATH"))    

from ucp_client import UCPMerchantRegistry

def search_ramdev_products(query=""):
    print(f"Initializing Registry...")
    registry = UCPMerchantRegistry()
    
    # Use the aliased name as requested by User
    client = registry.get_client("ramdev")
    if not client:
        print("Error: 'ramdev' client not found.")
        return

    print(f"Searching 'ramdev' for: '{query}'...")
    products = client.search_products(query=query)
    
    if products:
        print(f"Found {len(products)} products:")
        for p in products:
            print(f"- [{p.id}] {p.name} ({p.price} {p.currency})")
    else:
        print("No products found.")

if __name__ == "__main__":
    search_query = "charger" # Default or take from arg
    if len(sys.argv) > 1:
        search_query = sys.argv[1]
        
    search_ramdev_products(search_query)
