using System.Collections.Generic;
using UnityEngine;

public class ScreenManager : MonoBehaviour   // must inherit MonoBehaviour
{
    [SerializeField] List<GameObject> screens;
    [SerializeField] int defaultIndex = 0;

    void Awake() => ShowByIndex(defaultIndex);

    public void ShowByIndex(int index)
    {
        for (int i = 0; i < screens.Count; i++)
            screens[i].SetActive(i == index);
    }

    public void ShowWallet()            => ShowByIndex(0);
    public void ShowForecast()          => ShowByIndex(1);
    public void ShowTransactionLedger() => ShowByIndex(2);
    public void ShowModifier()          => ShowByIndex(3);
}
