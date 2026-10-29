from pathlib import Path
from recommender import read_purchases, RecommendationEngine

DATA_PATH = Path('data') / 'purchases.csv'
OUTPUT_PATH = Path('output') / 'recommendations.csv'



def main():
    valid_purchases, rejected_purchases = read_purchases(DATA_PATH)

    print(f'Valid purchases: {len(valid_purchases)}')
    print(f'Rejected purchases: {len(rejected_purchases)}')

    engine = RecommendationEngine(valid_purchases)
    print(f'Customers found: {len(engine.customer_products)}')
    print('\nCUSTOMER PURCHASE HISTORIES')

    for customer_id in sorted(engine.customer_products):
        products = engine.history(customer_id)
        customer_name = engine.get_customer_name(customer_id)

        print(f'\nCustomer: {customer_name} (ID: {customer_id})')
        print(f'Products purchased: {sorted(products)}')

    print(f'\nCUSTOMER SIMILARITY MATRIX')

    customer_ids = sorted(engine.customer_products)[:5]

    print(f'Customer IDS: {customer_ids}')

    for customer_a in customer_ids:
        row = []

        for customer_b in customer_ids:
            similarity_score = engine.similarity(customer_a, customer_b)
            row.append(f'{similarity_score:.2f}')

        print(f'{customer_a}: {row}')

    print(f'\nSIMILAR CUSTOMERS')

    for customer_id in sorted(engine.customer_products):
        similar = engine.similar_customers(customer_id, k=3)

        print(f'\nCustomer: {customer_id}')

        if not similar:
            print('No similar customers found')
            continue

        for neighbour_id, similarity_score in similar:
            print(
                f' Similar customer: {neighbour_id}'
                f'| Similarity: {similarity_score:.2f}'
            )

    print(f'\nPRODUCT RECOMMENDATIONS')

    for customer_id in sorted(engine.customer_products):
        recommendations = engine.recommend(customer_id, n=3)

        customer_name = engine.get_customer_name(customer_id)
        print(f'\nCustomer: {customer_name} (ID: {customer_id})')

        if not recommendations:
            print('No recommendations available')
            continue

        for recommendation in recommendations:
            
            print(
                f"Rank: {recommendation['rank']} "
                f"| Product: {recommendation['product_name']} "
                f"| Category: {recommendation['category']} "
                f"| Score: {recommendation['score']:.3f} "
                f"| Supporting customers: "
                f"{recommendation['supporting_customers']}"
            )

          

    all_recommendations = engine.recommend_all(n=3)
    engine.export_csv(all_recommendations, OUTPUT_PATH)

    print('\nSUMMARY')
    print(f'Total customers: {len(engine.customer_products)}')
    print(f'Valid purchases: {len(valid_purchases)}')
    print(f'Rejected purchases: {len(rejected_purchases)}')
    print(f'Recommendations generated: {len(all_recommendations)}')

    
if __name__ == '__main__':
    main()

