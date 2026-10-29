"""
Day 4 - Customer Recommendation Engine
Squad Python Specialization - Data Science, AI & Analytics

Core Python only for the engine (csv, collections, math are fine). No ML libraries.
"""
from __future__ import annotations

import csv
from pathlib import Path

DATA_PATH = Path("data") / "purchases.csv"
OUTPUT_PATH = Path("output") / "recommendations.csv"


def read_purchases(path: Path = DATA_PATH) -> tuple[list[dict], list[dict]]:
    """Return (valid_rows, rejected_rows). Decide what makes a purchase row unusable."""
    valid_rows = []
    rejected_rows = []
    seen_ids = set()

    with open(path, 'r', newline='') as file:
        reader = csv.DictReader(file)

        for row in reader:
            purchase_id = row['purchase_id'].strip()
            customer_id = row['customer_id'].strip()
            product_id = row['product_id'].strip()
            product_name = row['product_name'].strip()
            category = row['category'].strip()
            quantity = row['quantity'].strip()

            if not purchase_id or not customer_id or not product_id:
                row['rejection_reason'] = 'Missing purchase, customer or product ID'
                rejected_rows.append(row)
                continue

            if not product_name or not category:
                row['rejection_reason'] = 'Missing product name or category'
                rejected_rows.append(row)
                continue

            if purchase_id in seen_ids:
                row['rejection_reason'] = 'Duplicate purchase ID'
                rejected_rows.append(row)
                continue

            seen_ids.add(purchase_id)

            try:
                quantity = int(quantity)
            except ValueError:
                row['rejection_reason'] = 'Quantity is not a valid integer'
                rejected_rows.append(row)
                continue

            if quantity <= 0:
                row['rejection_reason'] = 'Quantity must be greater than zero'
                rejected_rows.append(row)
                continue

            row['purchase_id'] = purchase_id
            row['customer_id'] = customer_id
            row['product_id'] = product_id
            row['product_name'] = product_name
            row['category'] = category
            row['quantity'] = quantity

            valid_rows.append(row)

    return valid_rows, rejected_rows


def jaccard(a: set, b: set) -> float:
    """|A intersection B| / |A union B|. Define (and test) what happens when both are empty."""
    union = a | b

    if not union:
        return 1.0

    intersection = a & b
    return len(intersection) / len(union)


class RecommendationEngine:
    """Recommends products a customer has not bought, based on similar customers."""

    def __init__(self, purchases: list[dict], min_similarity: float = 0.0) -> None:
        self.min_similarity = min_similarity

        self.customer_products = {}
        self.product_names = {}
        self.product_categories = {}
        self.product_popularity = {}
        self.customer_names = {}

        for row in purchases:
            customer_id = row['customer_id']
            product_id = row['product_id']

            if customer_id not in self.customer_products:
                self.customer_products[customer_id] = set()

            self.customer_products[customer_id].add(product_id)

            self.customer_names[customer_id] = row['customer_name'].strip()
            self.product_names[product_id] = row['product_name']
            self.product_categories[product_id] = row['category']

            if product_id not in self.product_popularity:
                self.product_popularity[product_id] = 0

            self.product_popularity[product_id] += 1

            
    def history(self, customer_id: str) -> set[str]:
        if customer_id not in self.customer_products:
            raise KeyError(f'Unknown customer ID: {customer_id}')

        return self.customer_products[customer_id]


    def get_customer_name(self, customer_id: str) -> str:
        if customer_id not in self.customer_names:
            raise KeyError(f'Unknown customer ID: {customer_id}')

        return self.customer_names[customer_id]
    

    def similarity(self, customer_a: str, customer_b: str) -> float:
        history_a = self.history(customer_a)
        history_b = self.history(customer_b)

        return jaccard(history_a, history_b)
    

    def similar_customers(self, customer_id: str, k: int = 3) -> list[tuple[str, float]]:
        """Return the k most similar other customers as (customer_id, score), best first."""
        self.history(customer_id)

        if k <= 0:
            return []

        similarities = []

        for other_id in self.customer_products:
            if other_id == customer_id:
                continue

            similarity_score = self.similarity(customer_id, other_id)

            if similarity_score < self.min_similarity:
                continue

            similarities.append((other_id, similarity_score))

        similarities.sort(key=lambda item: (-item[1], item[0]))

        return similarities[:k]


    def candidate_products(self, customer_id: str, k: int = 3) -> dict[str, dict]:
        """Products bought by similar customers but not by this one, with the evidence for each."""
        customer_history = self.history(customer_id)
        neighbours = self.similar_customers(customer_id, k)

        candidates = {}

        for neighbour_id, similarity_score in neighbours:
            neighbour_history = self.history(neighbour_id)

            for product_id in neighbour_history:
                if product_id in customer_history:
                    continue

                if product_id not in candidates:
                    candidates[product_id] = {
                        'product_id' : product_id,
                        'similarity_total' : 0.0,
                        'supporting_customers' : []
                    }

                candidates[product_id]['similarity_total'] += similarity_score
                candidates[product_id]['supporting_customers'].append(neighbour_id)

        if not candidates:
            for product_id in self.product_popularity:
                if product_id not in customer_history:
                    candidates[product_id] = {
                        'product_id' : product_id,
                        'similarity_total' : 0.0,
                        'supporting_customers' : [],
                        'fallback' : True
                    }   

        return candidates



    def score(self, evidence: dict) -> float:
        """Your ranking rule. Combine similarity with at least one other signal."""
        similarity_total = evidence['similarity_total']

        if self.product_popularity:
            max_popularity = max(self.product_popularity.values())
            product_id = evidence['product_id']

            if max_popularity > 0:
                popularity_score = (
                    self.product_popularity[product_id] / max_popularity
                )
            else:
                popularity_score = 0.0
        else:
            popularity_score = 0.0

        if evidence.get('fallback', False):
            return 0.3 * popularity_score

        return 0.7 * similarity_total + 0.3 * popularity_score


    def recommend(self, customer_id: str, n: int = 3) -> list[dict]:
        """Return up to n ranked recommendations for one customer."""
        self.history(customer_id)

        if n <= 0:
            return []

        candidates = self.candidate_products(customer_id)
        recommendations = []

        for product_id, evidence in candidates.items():
            evidence['product_id'] = product_id

            recommendation_score = self.score(evidence)

            recommendations.append({
                'customer_id' : customer_id,
                'product_id' : product_id,
                'product_name' : self.product_names[product_id],
                'category' : self.product_categories[product_id],
                'score': recommendation_score,
                'supporting_customers': evidence['supporting_customers']
            })

        recommendations.sort(
            key=lambda item: (-item['score'], item['product_id'])
        )

        for rank, recommendation in enumerate(recommendations[:n], start=1):
            recommendation['rank'] = rank

        return recommendations[:n]
    


    def recommend_all(self, n: int = 3) -> list[dict]:
        all_recommendations = []

        for customer_id in sorted(self.customer_products):
            recommedations = self.recommend(customer_id, n)
            all_recommendations.extend(recommedations)

        return all_recommendations

    def export_csv(self, rows: list[dict], path: Path = OUTPUT_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        rows_written = 0

        fieldnames = [
            "customer_id",
            "customer_name",
            "rank",
            "product_id",
            "product_name",
            "category",
            "score",
            "supporting_customers"
        ]

        rows_by_customer = {}

        for row in rows:
            customer_id = row["customer_id"]

            if customer_id not in rows_by_customer:
                rows_by_customer[customer_id] = []

            rows_by_customer[customer_id].append(row)

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for customer_id in sorted(self.customer_products):
                customer_rows = rows_by_customer.get(customer_id, [])

                if not customer_rows:
                    writer.writerow({
                        "customer_id": customer_id,
                        "customer_name": self.get_customer_name(customer_id),
                        "rank": "",
                        "product_id": "",
                        "product_name": "",
                        "category": "",
                        "score": "",
                        "supporting_customers": ""
                    })

                    rows_written += 1
                    continue

                for row in customer_rows:
                    writer.writerow({
                        "customer_id": customer_id,
                        "customer_name": self.get_customer_name(customer_id),
                        "rank": row["rank"],
                        "product_id": row["product_id"],
                        "product_name": row["product_name"],
                        "category": row["category"],
                        "score": row["score"],
                        "supporting_customers": ", ".join(
                            row["supporting_customers"]
                        )
                    })

                    rows_written +=1

        print(f"Recommendations exported to: {path}")
        print(f"CSVrows writen: {rows_written}")
        print(f"Recommendation rows written: {sum(len(customer_rows) for customer_rows in rows_by_customer.values())}")


if __name__ == "__main__":
    valid, rejected = read_purchases()
    print(f'Valid: {len(valid)}')
    print(f'Rejected: {len(rejected)}')

    for row in rejected:
        print(row['purchase_id'], '-', row['rejection_reason'])

    print(f'Test 1: {jaccard({'P1', 'P2'}, {'P2', 'P3'})}')
    print(f'Test 2: {jaccard({'P1'}, {'P1'})}')
    print(f'Test 3: {jaccard(set(), set())}')


   