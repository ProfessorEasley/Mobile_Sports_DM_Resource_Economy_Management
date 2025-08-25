public class EconomyManager : MonoBehaviour
{
    public int coins = 10000;
    public int gems = 20;
    public int credits = 100;

    public LedgerUI ledgerUI;  // reference to your Ledger UI
    public WalletUI walletUI;  // reference to your Wallet UI

    public void AddTransaction(int amount, string type, string reason)
    {
        coins += amount;  // update value
        walletUI.UpdateWallet(coins, gems, credits); // refresh wallet panel
        ledgerUI.AddEntry($"{(amount >= 0 ? "+" : "-")} {Mathf.Abs(amount)} {type} - {reason}");
    }
}
