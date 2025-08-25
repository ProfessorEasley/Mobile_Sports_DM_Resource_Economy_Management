using UnityEngine;
using TMPro;

public class LedgerUI : MonoBehaviour
{
    public Transform contentParent;     // assign Content object
    public GameObject entryPrefab;      // assign a TMP text prefab

    public void AddEntry(string entry)
    {
        GameObject newText = Instantiate(entryPrefab, contentParent);
        newText.GetComponent<TextMeshProUGUI>().text = entry;
    }
}
