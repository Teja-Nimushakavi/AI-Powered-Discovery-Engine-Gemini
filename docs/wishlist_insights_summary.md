# Myntra RAG Discovery Engine: Key Insights & Hypotheses

This document summarizes the core findings extracted from 1,000 authentic consumer reviews regarding "Wishlist to Purchase" friction on Myntra.

## 1. Top Purchase-Barrier Frequencies
The percentage represents how frequently this specific friction point was mentioned among the relevant reviews (users who hesitated or abandoned a purchase).

* **Reviews/Ratings (75.8%):** Users hesitate to buy without strong social proof (customer photos/detailed reviews).
* **Availability (73.8%):** Highly desired sizes/colors go out of stock exactly when prices drop.
* **Price (69.1%):** High base costs, non-refundable platform fees, or finding cheaper alternatives on competitor platforms (like Ajio).
* **Size/Fit (54.8%):** Uncertainty about whether the item will actually fit based on the studio model images.
* **Delivery (54.9%) & Trust (42.8%):** Fear that Myntra will unexpectedly cancel the order or severely delay the delivery.
* **Appearance (71.4%) & Quality (22.4%):** Anxiety that the real product will look cheap or entirely different from the photos.

---

## 2. Core PM Hypotheses (Prioritized)
Based on the barriers above, the AI Engine synthesized the following top 3 actionable product hypotheses.

### **Priority 1 (P1): Delivery Trust Issues (54.9% Impact)**
* **The Hypothesis:** Users keep items in their wishlist because they are afraid Myntra will suddenly cancel their order or delay the delivery for weeks.
* **Why it matters:** Even if the price and availability are perfect, a fundamental lack of trust in the platform's ability to fulfill the order completely kills the conversion.
* **Validation Idea:** Test if implementing a "Guaranteed Delivery Date" badge with compensation for delays increases wishlist conversions.

### **Priority 2 (P2): Fear of Bad Returns & Support (71.4% Impact)**
* **The Hypothesis:** Users hesitate to buy because they worry the clothes will look cheap in real life, and they know getting a refund from the AI customer support bot is incredibly frustrating.
* **Why it matters:** The anxiety of receiving a defective item is amplified when the user feels trapped by an automated, unhelpful return loop.
* **Validation Idea:** Test if offering "1-Click Human Support" or a "No-Questions Return Guarantee" on wishlist items mitigates this barrier.

### **Priority 3 (P3): Hidden Fees & Waiting for Sales (69.1% Impact)**
* **The Hypothesis:** Users abandon their carts because they are waiting for massive sales to drop, or they get angry when a non-refundable "platform fee" is suddenly added at the very end of checkout.
* **Why it matters:** Reaching the final payment screen only to be hit with a non-refundable convenience fee creates immediate "price shock," sending the user straight back to the wishlist.
* **Validation Idea:** Test if offering "Platform Fee Waivers" for first-time wishlist conversions or triggering smart "Price Drop Alerts" increases purchase rates.
