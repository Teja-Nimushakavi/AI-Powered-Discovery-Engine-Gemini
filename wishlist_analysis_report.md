# Wishlist to Purchase Analysis Report

## 1. Dataset Overview & Relevance Analysis
- **Total Reviews Analysed**: 1000
- **Directly Relevant**: 331
- **Indirectly Relevant**: 626
- **Not Relevant**: 43
- **Relevance Percentage**: 95.70%

## 2. Purchase-Barrier Frequency
- Reviews/ratings: 726 (75.86%)
- Availability: 707 (73.88%)
- Product appearance: 684 (71.47%)
- Price: 662 (69.17%)
- Recommendations: 552 (57.68%)
- Delivery: 526 (54.96%)
- Size/Fit: 525 (54.86%)
- Trust: 410 (42.84%)
- Product comparison: 402 (42.01%)
- Product discovery: 375 (39.18%)
- Return/Exchange: 249 (26.02%)
- Quality uncertainty: 215 (22.47%)
- Discount waiting: 160 (16.72%)
- Choice overload: 125 (13.06%)

## 3. User Behaviour Frequency
- Purchased: 922 (96.34%)
- Compared products: 812 (84.85%)
- Wishlisted/Saved: 769 (80.36%)
- Considered but didn't buy: 391 (40.86%)
- Waiting: 131 (13.69%)

## 4. PM Hypotheses & Product Opportunity
Based on the provided customer feedback, users are experiencing significant post-purchase and checkout friction. While the feedback does not explicitly mention the word "wishlist," as a Product Manager, we can hypothesize that these severe friction points (such as sudden cancellations, delivery failures, quality issues, and customer support loops) create a lack of trust that discourages users from converting their wishlisted items into actual purchases. 

Here is the PM Hypotheses Report based strictly on the provided feedback:

---

### **H1: Trust Deficit due to Sudden Order Cancellations and Delivery Failures**
* **We believe that** the fear of sudden order cancellations and extreme delivery delays **is a major reason users do not purchase wishlisted products because** they do not trust Myntra to reliably deliver their orders, making them hesitant to commit their money.
* **Evidence:** 
  * Multiple users reported that Myntra cancelled their orders without proper reasons or due to "operational constraints" after making them wait (Chunk 1, Chunk 23, Chunk 42).
  * Users reported severe delivery delays (weeks past the promised date) and being repeatedly asked to wait another 24–48 hours due to "high volume" (Chunk 10).
* **What needs validation:** We need to validate if wishlist-to-purchase drop-offs are higher for time-sensitive items (e.g., festival wear, gifts) and if displaying a "Guaranteed Delivery" badge or real-time stock availability on the wishlist page increases conversion.

---

### **H2: Anxiety Over Deteriorating Product Quality and "AI-Only" Customer Support Loops**
* **We believe that** anxiety over receiving incorrect/poor-quality products and getting stuck in automated customer support loops **is a major reason users do not purchase wishlisted products because** they fear they will be left with a wrong or defective item and no way to get a refund or exchange.
* **Evidence:** 
  * Users reported receiving products of different brands than ordered, missing tags, and deteriorated quality (Chunk 3).
  * Users expressed extreme frustration that customer support is entirely automated ("goes straight to AI") with no resolution, and that they get stuck in endless loops where calls are disconnected and refunds/returns are not processed (Chunk 3, Chunk 28).
* **What needs validation:** We need to validate whether users who have previously experienced a return/refund issue have lower wishlist-to-purchase conversion rates compared to those who haven't, and if offering a "1-Click Human Support Guarantee" or "Quality Assured" badge on wishlist items mitigates this barrier.

---

### **H3: Price Friction from Non-Refundable Platform Fees**
* **We believe that** the addition of high, non-refundable platform fees at checkout **is a major reason users do not purchase wishlisted products because** it increases the perceived cost of the product at the final step, causing immediate cart/wishlist abandonment.
* **Evidence:** 
  * A user specifically complained about a "very High platform Fee" that was "not refunded" (Chunk 46).
* **What needs validation:** We need to validate if users are dropping off at the final payment screen specifically when the platform fee is added, and if offering platform fee waivers (e.g., for first-time wishlist conversions or loyalty members) improves purchase rates.

---

### **Distinction Between Evidence and Assumptions**
* **Evidence (Facts from Chunks):** Users are experiencing sudden order cancellations, delayed deliveries, incorrect items, unhelpful AI customer service, and non-refundable platform fees.
* **Assumptions (Hypotheses to Test):** We are *assuming* that these negative post-purchase experiences and platform policies are actively discouraging users from converting their wishlisted items. We must validate whether resolving these specific pain points directly correlates with an increase in wishlist-to-purchase conversion rates.