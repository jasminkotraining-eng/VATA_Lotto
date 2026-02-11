# VATA_Lotto, VATA_Validator and VATA_SimPro: Complete User Guide
*Conceptualized by the Author of the "Last Run" theory | Developed with Google Gemini AI*

---

## 📋 Contents
1. [The "Last Run" Philosophy](#philosophy)
2. [VATA Concept Explained](#vata-concept)
3. [Binary Prediction Logic](#binary)
4. [Setting Up Your Laboratory](#setup)
5. [Deep Dive: Understanding Filter Tables](#tables)
6. [Optimization Engine & Pooling](#optimization)
7. [VATA_Validator: Finding the Sweet Spot](#validator)
8. [VATA_SimPro: The Simulator](#simulator)
9. [Technical Notes & Author's Disclaimer](#technical)

---

<a name="philosophy"></a>
## 1. The "Last Run" Philosophy
Traditional lottery analysis is often misleading because it focuses on the "Law of Large Numbers" over thousands of draws. **VATA_Lotto** operates on a different principle: **The Nature and Trend of the Recent Run.**

We don't care if a number is "due" because it hasn't appeared in a year. We care about its current behavior. Is it in a "Hit" streak or a "Skip" streak? How does its current streak compare to its own historical average? 

Most software will tell you: *"Odd sums haven't appeared in 6 draws, they are due!"* **VATA_Lotto goes a step further:** It counts the number of runs throughout history, calculates the average length of those runs (AvgRun), and compares it to the undecided **Recent Run**. 

<a name="vata-concept"></a>
## 2. VATA Concept (Volatility, Average, Trend Analysis)
The whole concept boils down to finding the right set of parameters to answer a crucial question: **Is the current streak going to Continue or is it going to Break?**

* **Volatility (V):** Measures how consistent a number’s streaks are.
* **Average (A):** The historical average of streaks with the same sign (excluding the undecided Recent run).
* **Trend (T):** Regardless of $R/A$ and Volatility, are there signs of the item slowing down or advancing in the last 20, 30, or $N$ draws?

<a name="binary"></a>
## 3. Binary Prediction Logic (The Switch Table)
To simplify complex data, we use symbolic representation:
* **11:** Represents a Hit streak (e.g., +1 or +5).
* **00:** Represents a Skip streak (e.g., -1 or -11).

| Current State | Symbol | Predicted Outcome | Play? |
| :--- | :--- | :--- | :--- |
| **00** (Skip run) | `000` | Continues (Wait longer) | No |
| **00** (Skip run) | `001` | **Breaks** (Hit Expected) | **YES** |
| **11** (Hit run) | `110` | **Breaks** (Skip Expected) | No |
| **11** (Hit run) | `111` | Continues (Hit Streak) | **YES** |

---

<a name="setup"></a>
## 4. Setting Up Your Laboratory
1. **Define the Game:** Set **Nums** (total balls) and **Draw** (balls per line). Default is 6/39.
2. **Load History:** Paste or import your history file.

> ### 📊 Preparing History Files
> To analyze trends, you need to provide a history of past winning combinations in a plain text file (`.txt`).
> 
> **Important Formatting Rules:**
> * **Numbers Only:** Use only combinations (5, 6, or 7 numbers per line).
> * **No Metadata:** Do not include ticket numbers, dates, or days.
> * **Chronology:** The software reads from top to bottom. Ensure the **most recent combinations are at the bottom** of the file.
> * **Example:** >   `4, 12, 18, 22, 35, 39`  
>   `1, 7, 19, 25, 30, 32` (Latest draw)

3. **Validate:** The system checks if data is valid (integers, no duplicates).
4. **Analysis Parameters:** Set Trend Window (5-500), Trend Weight, and Volatility Penalty.

---

<a name="tables"></a>
## 5. Deep Dive: Understanding Filter Tables

Every filter window (Numbers, Sums, Patterns, etc.) contains a detailed analytical table. Each column can be sorted by clicking the header to identify trends quickly.

    Col 1 (Items): The specific numbers, sums, or patterns being analyzed.

    Col 2 (Sel): Selection checkbox. Use "Invert Selection" or "Select All" for bulk actions.

    Col 3 (Theo%): Theoretical probability of the item (e.g., a single number in 6/39 has a 2.56% chance per draw).

    Col 4-5 (Expected/Empirical): Mathematical expectation based on history length vs. how many times it actually appeared.

    Col 6 (E-E): The raw difference (Efficiency Gap). Note: VATA focuses on the Recent Run rather than waiting for this gap to close.

    Col 7 (Recent): The current, undecided run. Shows how many draws the item has been continuously Hitting (+) or Skipping (-).

    Col 8 (AvgRun): The historical average length of all previous completed runs (signed + or -).

    Col 9 (R/A): Recent/Average Relation. A value >1 means the current run is longer than the historical average (it is "overdue" to break).

    Col 10 (Vol): Volatility. Measures the consistency of streaks. Low volatility suggests a more "reliable" trend.

    Col 11 (Trend): Momentum calculated over the specific "Trend Window" (e.g., last 100 draws).

    Col 12 (Composite Index): The "Heart" of the system. A weighted score combining R/A, Volatility, and Trend.

    Col 13-14 (Symbol & Play?): * 111 / 001: Strong signals to play (Continue Hit or Break Skip).

        110 / 000: Signals to avoid (Break Hit or Continue Skip).

---

<a name="optimization"></a>
## 6. Optimization Engine & Pooling
**Fill the Pool:** Choose source (Filters, History, or Random/File).
**Optimize:**
* **Deterministic:** Exactly matches your committed filters.
* **Heuristic:** Smart search for best-fit combinations.
* **Cumulative Contribution:** Shows coverage percentage (T1, T2...).

---

<a name="validator"></a>
## 7. VATA_Validator: Finding the Sweet Spot
Find which parameters actually work for your specific lottery.
* **Test Count:** How many times to repeat the test going back in history.
* **Deep Optimize:** Automatically tries different weights to find the most hits.
* **Comparison:** Check if **Play** numbers outperformed **Random** numbers.

---

<a name="simulator"></a>
## 8. VATA_SimPro: The Simulator
* Simulate any game format (5/18, 6/45, 7/42...).
* **Important:** Use the **Sort** button before copying data to the Lab or Validator.

---

<a name="technical"></a>
## 9. Technical Notes & Author's Disclaimer
**Development Note:** This program was developed by translating my "Last Run" theory into code using **Google Gemini AI**.

**Important:** To ensure Copy/Paste works perfectly, **DO NOT run via Python IDLE**. Run by double-clicking the `.py` files directly.

*Note: Frequency statistics should have low weight (e.g., 20%), as randomness is not bound by history.*