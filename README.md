# Day 4 Customer Purchase Recommendation System

## 1. Project Overview

This project implements a customer product recommendation system using purchase history data. It identifies customers with similar purchasing behaviour and recommends products that a customer has not purchased.

The system also uses product popularity to help rank recommendations, handles invalid purchase records, and exports the results to a CSV file.

### Objectives

- Load and validate purchase data from a CSV file.
- Separate valid purchases from rejected records.
- Build customer purchase histories and product statistics.
- Calculate customer similarity using Jaccard similarity.
- Identify the most similar customers.
- Generate and score product recommendations.
- Export recommendations for every customer to a CSV file.
- Display customer histories, similarity scores,  recommendations, and a summary.

## 2. Project Structure

The project uses the following folder structure:

```text
day4-project/
├── data/
│   └── purchases.csv
├── output/
│   └── recommendations.csv
├── recommender.py
├── main.py
├── README.md
└── requirements.txt
```

### File descriptions

- `data/purchases.csv`: Contains the original purchase records.
- `recommender.py`: Contains the data validation function, Jaccard similarity function, recommendation engine, scoring logic, and CSV export method.
- `main.py`: Runs the complete recommendation program and displays the results.
- `output/recommendations.csv`: Stores the generated recommendations.
- `requirements.txt`: Lists the project's dependencies.

The output CSV is created automatically if the `output` directory does not already exist.

## 3. Requirements

- Python.
- A CSV file containing the purchase data.
- No external packages are required.

The project uses standard library modules such as `csv` and `pathlib`.

## 4. Input Data

The input file is `data/purchases.csv`.

The expected columns are:

| Column | Description |
|---|---|
| `purchase_id` | Unique identifier for a purchase record |
| `customer_id` | Identifier of the customer |
| `customer_name` | Customer's name |
| `product_id` | Identifier of the purchased product |
| `product_name` | Name of the purchased product |
| `category` | Product category |
| `purchase_date` | Date of purchase |
| `quantity` | Quantity purchased |

The program reads the CSV file using `csv.DictReader`.

## 5. Data Validation

The `read_purchases()` function reads the input data and returns two collections: valid purchase records and rejected purchase records.

Each record is checked against the following validation rules.

| Validation rule | Reason for rejection |
|---|---|
| Purchase ID must not be empty | Missing purchase ID |
| Customer ID must not be empty | Missing customer ID |
| Product ID must not be empty | Missing product ID |
| Product name must not be empty | Missing product name |
| Category must not be empty | Missing category |
| Purchase ID must be unique | Duplicate purchase ID |
| Quantity must be a valid integer | Invalid quantity |
| Quantity must be greater than zero | Non-positive quantity |

Rejected records are assigned a `rejection_reason` explaining why they were rejected.

Valid records are used to build the recommendation engine. Rejected records are excluded from recommendation calculations.

The program reports the number of valid and rejected records after loading the data.

## 6. Recommendation Engine

The `RecommendationEngine` class processes valid purchase records and organizes the information needed to generate recommendations.

During initialization, it creates the following data structures:

- **Customer purchase histories:** Stores the unique product IDs purchased by each customer.
- **Customer names:** Stores each customer's name alongside their customer ID.
- **Product names:** Stores each product's name alongside its product ID.
- **Product categories:** Stores each product's category alongside its product ID.
- **Product popularity:** Counts how many valid purchase records are associated with each product.

These data structures make it easier to retrieve customer and product information when calculating similarities and generating recommendations.

Customer purchase histories use sets to avoid storing the same product ID more than once for a customer.

Product popularity is based on the number of valid purchase records, rather than the total quantity purchased.

The class also provides methods for retrieving purchase histories, calculating customer similarity, finding similar customers, generating candidate products, calculating recommendation scores, and exporting recommendations.

## 7. Customer Similarity

### Jaccard similarity

The system uses Jaccard similarity to compare customers based on their unique purchased products.

The formula is:

\[
J(A,B)=\frac{|A\cap B|}{|A\cup B|}
\]

Where:

- \(A\) is the set of products purchased by the first customer.
- \(B\) is the set of products purchased by the second customer.
- \(A\cap B\) represents the products both customers purchased.
- \(A\cup B\) represents all unique products purchased by either customer.

The similarity score ranges from 0 to 1.

- A score of `1.0` means the customers have identical product sets.
- A score of `0.0` means they have no products in common, provided their combined product set is non-empty.
- A score between `0.0` and `1.0` indicates partial overlap.

If both customers have no purchased products, the function returns `1.0`. However, every customer in this project should have at least one valid purchase so this situation is not expected.

### Example

- Customer A purchased `{P1, P2}`.
- Customer B purchased `{P2, P3}`.

Their intersection is `{P2}`, containing one product. Their union is `{P1, P2, P3}`, containing three products.

Therefore:

\[
J(A,B)=\frac{1}{3}\approx0.3333
\]

The similarity score is approximately `0.33`.

### Similar customer selection

The `similar_customers(customer_id, k)` method:

1. Compares the selected customer with every other customer.
2. Excludes the customer from their own neighbour list.
3. Applies the configured minimum similarity threshold.
4. Sorts the remaining customers by similarity, highest first.
5. Uses customer ID as a tie-breaker to produce deterministic ordering.
6. Returns at most `k` similar customers.

The main program displays a similarity matrix for the first five customer IDs in sorted order and lists the three most similar customers for each customer.

## 8. Candidate Product Generation

The `candidate_products(customer_id, k)` method identifies products that may be recommended to a customer.

It uses the following approach:

1. Retrieves the customer's purchase history.
2. Finds the customer's top `k` similar customers.
3. Examines the products purchased by those neighbours.
4. Excludes products the target customer has already purchased.
5. Collects evidence for each remaining product.
6. Adds the similarity scores of neighbours who support each candidate.
7. Records the IDs of customers who support each recommendation.

The supporting customer IDs provide evidence for why a product was suggested.

### Fallback strategy

If the neighbour-based approach produces no candidate products, the system falls back to products that the target customer has not purchased.

These fallback candidates are ranked using product popularity.

This approach provides recommendations when there are no qualifying neighbours or when the neighbours do not provide any new products to recommend.

If a customer has already purchased every available product, the system will return no recommendations.

## 9. Recommendation Scoring

The score(evidence) method calculates a score for each candidate product by combining customer similarity and product popularity. This helps the system recommend products that are both relevant to similar customers and frequently purchased.

For recommendations based on similar customers, the formula is:
\[
\text{Score}(p)=0.7T(p)+0.3P(p)
\]

Where:
- \(T(p)\) — Similarity Total: The sum of the similarity scores of all customers who support the recommendation.
- \(P(p)\) — Popularity Score: The number of valid purchase records for the product divided by the highest purchase-record count among all products.

The formula assigns 70% weight to similarity and 30% to popularity. Similarity receives more weight because the system aims to recommend products based on the purchasing behaviour of customers with similar interests.

#### Fallback scoring

If the system cannot find suitable products through similar customers, it uses product popularity to recommend products the customer has not purchased.

The fallback formula is:
\[
\text{Score}(p)=0.3P(p)
\]

In this case, only the popularity component contributes to the score because there is no supporting neighbour evidence.

#### Worked example

Suppose a candidate product has a similarity total of `1.0`, five purchase records and the most popular product has ten purchase records.

First, calculate the popularity score:
\[
P(p)=\frac{5}{10}=0.5
\]

Then calculate the recommendation score:
\[
\begin{aligned}
\text{Score}(p)&=0.7(1.0)+0.3(0.5)\\
&=0.7+0.15\\
&=0.85
\end{aligned}
\]

The final recommendation score is 0.85.

Products are ranked from the highest score to the lowest, with product ID used to break ties. These scores are used to compare and rank recommendations; they are not probabilities of a customer purchasing a product. Because similarity scores are added across supporting customers, the total recommendation score can exceed 1.0.


## 10. Generating Recommendations

The `recommend(customer_id, n)` method generates recommendations for one customer.

It:

1. Validates the customer ID.
2. Generates candidate products.
3. Calculates a score for each candidate.
4. Retrieves each product's name and category.
5. Includes the supporting customer IDs.
6. Sorts candidates by score, highest first.
7. Uses product ID as a deterministic tie-breaker.
8. Returns at most `n` recommendations with ranks starting at `1`.

The default workflow requests three recommendations per customer.

If the customer ID is unknown, the engine raises a `KeyError` with a descriptive message rather than silently returning an empty result.

The `recommend_all(n=3)` method generates recommendations for every customer in the engine and combines the results into one list.

## 11. Output CSV

The program exports the results to:

`output/recommendations.csv`

The expected columns are:

| Column | Description |
|---|---|
| `customer_id` | ID of the customer receiving the recommendation |
| `customer_name` | Customer's name |
| `rank` | Position of the recommendation |
| `product_id` | ID of the recommended product |
| `product_name` | Name of the recommended product |
| `category` | Category of the recommended product |
| `score` | Calculated recommendation score |
| `supporting_customers` | IDs of supporting customers |

Each recommended product occupies one row.

Every customer in the engine must appear in the CSV, including customers who receive no recommendations. For a customer with no recommendations, the export function writes one row containing the customer's ID and name, with the recommendation-specific fields left blank.

The export function also prints a summary showing:

- The output file path.
- The number of CSV data rows written.
- The number of actual recommendations written.

CSV row counts and recommendation counts may differ because customers without recommendations still receive a row in the output file.

## 12. How to Run the Project

Run the following steps from the project directory.

### Step 1: Open a terminal

Navigate to the `day4-project` folder, where `main.py` and `recommender.py` are located.

### Step 2: Run the program

Execute:

```bash
python main.py
```

### Step 3: Review the console output

The program displays:

1. Valid and rejected purchase counts.
2. The number of customers found.
3. Customer purchase histories.
4. The similarity matrix for the first five customers.
5. Similar customers and their similarity scores.
6. Product recommendations and their scores.
7. A run summary.

### Step 4: Review the output file

Open `output/recommendations.csv` in a spreadsheet application such as Microsoft Excel.

The file is overwritten when the program is run again.

## 13. Assumptions

The implementation uses the following assumptions:

- Only valid purchase records contribute to customer histories, popularity counts, and recommendations.
- Customer similarity is based on unique product IDs not purchase quantities.
- Product popularity is measured by the number of valid purchase records, not the total units sold.
- The default minimum similarity threshold is `0.0`, so customers with zero similarity may qualify as neighbours unless the threshold is configured differently.
- Recommendations exclude products already present in the target customer's purchase history.
- The default workflow requests three recommendations per customer.
- Product ID is used to break ties between candidates with equal scores.
- Fallback recommendations use product popularity when similar customers cannot provide new products.

## 14. Conclusion

This project implements a customer recommendation system using purchase history, Jaccard similarity, neighbour-based candidate generation, and product popularity.

It validates input records, identifies similar customers, recommends previously unpurchased products, ranks candidates using a weighted scoring method, and exports the results to a structured CSV file.

The code is organized into separate sections for data validation, recommendation generation, program execution, and exporting results. This makes the system easier to understand, test, maintain, and improve in the future.