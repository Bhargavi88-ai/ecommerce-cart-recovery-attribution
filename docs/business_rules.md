# Business Rules Specification
## E-Commerce Abandoned Cart Recovery and Campaign Attribution System

### 1. Cart Abandonment Rules

#### 1.1 Qualification Conditions
A shopping cart is classified as `ABANDONED` if and only if:
1. **Product Lines:** The cart contains at least 1 valid line item (`count(cart_lines) >= 1`).
2. **Not Purchased:** No completed order has been placed referencing this `cart_id`.
3. **Not Recovered:** The cart status is not currently `RECOVERED` (`recovered_at IS NULL`).
4. **Not Expired:** The cart is not explicitly expired or cancelled.
5. **Inactivity Period:** Time elapsed since the cart's latest activity meets or exceeds the inactivity threshold $\Delta t_{\text{inactivity}}$ (default: 60 minutes):
   $$\text{elapsed\_time} = t_{\text{reference}} - t_{\text{last\_activity}} \ge \Delta t_{\text{inactivity}}$$

#### 1.2 Calculated Abandonment Timestamp
The exact abandonment timestamp is deterministically calculated strictly from the cart's last activity:
$$t_{\text{abandoned}} = t_{\text{last\_activity}} + 60\text{ minutes}$$

---

### 2. Customer Consent & Privacy Rules

#### 2.1 Channel Independence
Consent for `EMAIL` and `SMS` is managed completely independently:
- A customer opting out of SMS does not suppress Email communications.
- A customer opting out of Email does not suppress SMS communications.

#### 2.2 Point-In-Time Effective Evaluation
Consent is evaluated at the exact dispatch attempt timestamp $t_{\text{attempt}}$:
$$\text{Consent}(t_{\text{attempt}}) = \operatorname{Latest}\left(\{ c \in \text{Consents}(\text{customer}, \text{channel}) \mid c.\text{effective\_at} \le t_{\text{attempt}} \}\right)$$
- If the latest effective record has status `OPT_IN`, the send is permitted.
- If the latest effective record has status `OPT_OUT`, the send is immediately suppressed.
- If no consent record exists, the send is suppressed with reason `NO_EMAIL_CONSENT` or `NO_SMS_CONSENT`.

---

### 3. Suppression & Frequency Capping Rules

#### 3.1 Frequency Cap
To prevent message fatigue, a customer may receive at most **3 recovery messages per channel within any rolling 7-day window**:
$$\sum_{s \in \text{Sends}(\text{customer}, \text{channel})} \mathbf{1}\left(s.\text{status} = \text{'SENT'} \land (t_{\text{attempt}} - 7\text{ days} \le s.\text{sent\_at} \le t_{\text{attempt}})\right) < 3$$
If the count reaches 3, the attempt is suppressed with `FREQUENCY_CAP_REACHED`.

#### 3.2 Prior Purchase Suppression
If an order was completed for this cart prior to $t_{\text{attempt}}$, the message is suppressed with `CART_PURCHASED`.

#### 3.3 Duplicate Campaign Variant Suppression
If the same campaign variant was already dispatched to this cart, the attempt is suppressed with `DUPLICATE_CAMPAIGN`.

---

### 4. Suppression Reason Code Catalog

| Reason Code | Condition Trigger |
|---|---|
| `NO_EMAIL_CONSENT` | No prior opt-in consent record for Email channel exists prior to send attempt. |
| `NO_SMS_CONSENT` | No prior opt-in consent record for SMS channel exists prior to send attempt. |
| `CONSENT_WITHDRAWN` | Customer explicitly opted out prior to the send attempt timestamp. |
| `CART_PURCHASED` | Cart was already converted into a completed order. |
| `FREQUENCY_CAP_REACHED` | Customer received 3 sent recovery messages in the past 7 rolling days on this channel. |
| `DUPLICATE_CAMPAIGN` | The cart has already received this exact campaign variant. |
| `CART_NOT_ABANDONED` | Inactivity period was not satisfied at evaluation time. |
| `INVALID_CONTACT` | Recipient email address or phone number is syntactically malformed. |
