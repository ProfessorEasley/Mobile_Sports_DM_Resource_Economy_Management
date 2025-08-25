using UnityEngine;

public class PanelInitializer : MonoBehaviour
{
    public Canvas mainCanvas;          // Drag your Canvas here in Inspector
    public GameObject[] panels;        // Drag all your screen panels here in Inspector

    void Start()
    {
        foreach (GameObject panel in panels)
        {
            // Set Canvas as parent
            panel.transform.SetParent(mainCanvas.transform, false);

            // Stretch panel to fill canvas
            RectTransform rect = panel.GetComponent<RectTransform>();
            rect.anchorMin = Vector2.zero;   // bottom-left
            rect.anchorMax = Vector2.one;    // top-right
            rect.offsetMin = Vector2.zero;   // reset left/bottom offset
            rect.offsetMax = Vector2.zero;   // reset right/top offset
        }
    }
}
