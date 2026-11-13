# Campaign Conversion Attribution Logic
## Deterministic Last-Click Lookback Model

### 1. Objective and Policy
Attribution links an incoming customer purchase order to marketing recovery campaigns. The system implements a **Deterministic Last-Click Attribution Model** to prevent double-counting order revenue and attribute credit to the proximate customer touchpoint.

---

### 2. Attribution Qualification Criteria
An order $O$ placed at $t_{\text{order}}$ qualifies for recovery attribution if and only if:
1. **Eligible Click Event:** There exists at least one communication event $E$ of type `CLICKED` associated with the customer's abandoned cart or customer profile.
2. **Strict Chronological Precedence:** The click event occurred strictly before the order placement:
   $$t_{\text{click}} < t_{\text{order}}$$
3. **Lookback Window:** The click occurred within the configured lookback window $\Delta t_{\text{window}}$ (default: 7 days / 168 hours):
   $$t_{\text{order}} - 7\text{ days} \le t_{\text{click}} < t_{\text{order}}$$

---

### 3. Last-Click Tie-Breaking & Selection Algorithm
When multiple campaign clicks qualify for the same order:
1. Compute the set of all qualified candidate clicks:
   $$\mathcal{C} = \{ c \in \text{Clicks}(O.\text{customer}) \mid t_{\text{order}} - 7\text{d} \le c.\text{timestamp} < t_{\text{order}} \}$$
2. The winning campaign is the one corresponding to the maximum timestamp:
   $$c^* = \operatorname{argmax}_{c \in \mathcal{C}} (c.\text{timestamp})$$
3. All other candidate clicks $c \in \mathcal{C} \setminus \{c^*\}$ are recorded as **competing claims** in analytical audit trails.

---

### 4. Non-Double-Counting Guarantee
- Each order $O$ can have at most **one primary attribution record**:
  $$\text{count}(\text{Attributions}(O)) \le 1$$
  Enforced by a database `UNIQUE` constraint on `attributions.order_id`.
- Total Attributed Revenue is strictly bounded by total completed order value:
  $$\sum_{a \in \text{Attributions}} a.\text{attributed\_revenue} \le \sum_{o \in \text{Orders}} o.\text{total\_amount}$$

---

### 5. Conversion Latency Metric
For every attributed order, the conversion latency is tracked in elapsed whole hours:
$$\text{latency\_hours} = \left\lfloor \frac{t_{\text{order}} - t_{\text{qualifying\_click}}}{3600\text{ seconds}} \right\rfloor$$
This provides visibility into customer decision turnaround across email vs SMS campaigns.
