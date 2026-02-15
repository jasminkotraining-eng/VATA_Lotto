# VATA_Lotto - User Guide

This guide explains how to use the VATA_Lotto suite to analyze, validate, and simulate lottery outcomes using the VATA (Volatility, Agility, Trend, Activity) methodology.

---

## 1. Core Philosophy: The VATA Methodology
VATA is a "ballistic" approach to lottery numbers, treating them as moving objects with momentum and trends rather than static probabilities.
* **V (Volatility):** Measure of how much a number "jumps" around its expected frequency.
* **A (Agility):** The speed of change in a number's behavior.
* **T (Trend):** The directional movement (upward or downward) of a number's appearance.
* **A (Activity):** The current "state" of the number in the recent draw cycle.

---

## 2. VATA_Lotto: Main Interface & Strategy
This is your primary tool for generating predictions.

* **Independence of History:** The software can be used even **without history**. If the history checkbox is unchecked, the user can still see **Theoretical Values** and make decisions based on mathematical probability and filter intersections.
* **Selected vs. Committed:** These functions are independent. You can "Commit" a strategy to the system, but still manually "Select" individual numbers to see how they impact the overall theoretical outcome.
* **The Composite Index (The "Master Score"):** The program calculates a single score for every number using the formula:
    `Composite = (w_R * R_norm) + (w_A * A) + (w_V * V) + (w_T * T)`
    *(Where `w` are weights and R,A,V,T are normalized VATA parameters).*
    A higher index means a number is "mathematically riper" for the next draw.

---

## 3. Binary Prediction Logic (The Switch Table)
VATA uses a binary system to track the status of numbers:
* **11:** Represents the most **RECENT** Hit streak (e.g., +1 or +5).
* **00:** Represents the most **RECENT** Skip streak (e.g., -1 or -11).
* **01:** Transition from Skip to Hit.
* **10:** Transition from Hit to Skip.

---

## 4. VATA_Validator: Testing the Theory
Use the Validator to prove the strategy against historical data.
* **Test Counts:** How many recent draws you want to use for the "exam" (e.g., last 50 draws).
* **Depth:** How many previous draws the program "looks back" at to calculate VATA parameters for *each* of those test draws.

### **Try This: The Power User Recipe**
1.  **Import history** from your local file.
2.  **Validate history** to see baseline performance.
3.  **Run Deep Optimize:** Let the computer find the perfect "AND-ing" (intersection) of filters.
4.  **Analyze Results:** At the bottom, compare these groups:
    * **Play:** Top 12/15/18 numbers with the BEST Composite index.
    * **Avoid:** Numbers with the WORST index (likely to stay dormant).
    * **Random:** A control group used to prove that VATA logic outperforms pure luck.

---

## 5. Filters inside Filters
This version includes 4 core filters: **Numbers, Sums, Patterns, and Repeats**. This is enough to test the "AND-ing" (intersection) logic.
* **Deep Analysis:** Every filter has its own VATA depth.
* **E & E-E columns:** Show Expected vs. Deviation values. Sort these to find "Hot" or "Cold" items within *any* filter.
* **Recent column:** Sort this to identify items that have been dormant for a long time or those currently in a "Hit" streak.

---

## 6. VATA_SimPro: Simulation & Integration
* **Point 8 Integration:** Generated combinations from SimPro can be copied and pasted directly back into **VATA_Lotto** for further filtering or into **VATA_Validator** for back-testing.
* **Algorithm Testing:** Use SimPro to see how your "AND-ing" strategy holds up over thousands of simulated draws.

---
