Here's a complete Unity C# implementation for a character stats system with all requested features:

```csharp
using System;
using UnityEngine;
using UnityEngine.UI;

[Serializable]
public class BaseStats
{
    public int hp = 100;
    public int mp = 50;
    public int attack = 20;
    public int defense = 10;
    public int speed = 15;
}

[Serializable]
public class EquipmentBonus
{
    public int hpBonus;
    public int mpBonus;
    public int attackBonus;
    public int defenseBonus;
    public int speedBonus;
}

public class CharacterStats : MonoBehaviour
{
    [Header("Base Stats")]
    public BaseStats baseStats;
    
    [Header("Level & XP")]
    public int currentLevel = 1;
    public int currentXP = 0;
    public int xpToNextLevel = 100;
    
    [Header("Equipment Bonuses")]
    public EquipmentBonus equipmentBonus;
    
    [Header("UI References")]
    public Text levelText;
    public Text xpText;
    public Text hpText;
    public Text mpText;
    public Text attackText;
    public Text defenseText;
    public Text speedText;
    
    // Calculated stats
    public int MaxHP { get; private set; }
    public int MaxMP { get; private set; }
    public int Attack { get; private set; }
    public int Defense { get; private set; }
    public int Speed { get; private set; }
    
    private const string SAVE_KEY = "CharacterStats";
    
    void Start()
    {
        LoadStats();
        CalculateStats();
        UpdateUI();
    }
    
    public void AddXP(int amount)
    {
        currentXP += amount;
        CheckLevelUp();
        UpdateUI();
        SaveStats();
    }
    
    void CheckLevelUp()
    {
        while (currentXP >= xpToNextLevel)
        {
            currentXP -= xpToNextLevel;
            LevelUp();
        }
    }
    
    void LevelUp()
    {
        currentLevel++;
        xpToNextLevel = (int)(xpToNextLevel * 1.5f);
        
        // Level up rewards
        baseStats.hp += 10;
        baseStats.mp += 5;
        baseStats.attack += 3;
        baseStats.defense += 2;
        baseStats.speed += 1;
        
        CalculateStats();
        UpdateUI();
        SaveStats();
        
        Debug.Log($"Level Up! Now Level {currentLevel}");
    }
    
    public void AddEquipmentBonus(EquipmentBonus bonus)
    {
        equipmentBonus.hpBonus += bonus.hpBonus;
        equipmentBonus.mpBonus += bonus.mpBonus;
        equipmentBonus.attackBonus += bonus.attackBonus;
        equipmentBonus.defenseBonus += bonus.defenseBonus;
        equipmentBonus.speedBonus += bonus.speedBonus;
        
        CalculateStats();
        UpdateUI();
        SaveStats();
    }
    
    public void RemoveEquipmentBonus(EquipmentBonus bonus)
    {
        equipmentBonus.hpBonus -= bonus.hpBonus;
        equipmentBonus.mpBonus -= bonus.mpBonus;
        equipmentBonus.attackBonus -= bonus.attackBonus;
        equipmentBonus.defenseBonus -= bonus.defenseBonus;
        equipmentBonus.speedBonus -= bonus.speedBonus;
        
        CalculateStats();
        UpdateUI();
        SaveStats();
    }
    
    void CalculateStats()
    {
        MaxHP = baseStats.hp + equipmentBonus.hpBonus;
        MaxMP = baseStats.mp + equipmentBonus.mpBonus;
        Attack = baseStats.attack + equipmentBonus.attackBonus;
        Defense = baseStats.defense + equipmentBonus.defenseBonus;
        Speed = baseStats.speed + equipmentBonus.speedBonus;
    }
    
    void UpdateUI()
    {
        if (levelText) levelText.text = $"Level: {currentLevel}";
        if (xpText) xpText.text = $"XP: {currentXP}/{xpToNextLevel}";
        if (hpText) hpText.text = $"HP: {MaxHP}";
        if (mpText) mpText.text = $"MP: {MaxMP}";
        if (attackText) attackText.text = $"Attack: {Attack}";
        if (defenseText) defenseText.text = $"Defense: {Defense}";
        if (speedText) speedText.text = $"Speed: {Speed}";
    }
    
    public void SaveStats()
    {
        PlayerPrefs.SetInt($"{SAVE_KEY}_Level", currentLevel);
        PlayerPrefs.SetInt($"{SAVE_KEY}_XP", currentXP);
        PlayerPrefs.SetInt($"{SAVE_KEY}_XPNext", xpToNextLevel);
        
        PlayerPrefs.SetInt($"{SAVE_KEY}_BaseHP", baseStats.hp);
        PlayerPrefs.SetInt($"{SAVE_KEY}_BaseMP", baseStats.mp);
        PlayerPrefs.SetInt($"{SAVE_KEY}_BaseAttack", baseStats.attack);
        PlayerPrefs.SetInt($"{SAVE_KEY}_BaseDefense", baseStats.defense);
        PlayerPrefs.SetInt($"{SAVE_KEY}_BaseSpeed", baseStats.speed);
        
        PlayerPrefs.SetInt($"{SAVE_KEY}_EquipHP", equipmentBonus.hpBonus);
        PlayerPrefs.SetInt($"{SAVE_KEY}_EquipMP", equipmentBonus.mpBonus);
        PlayerPrefs.SetInt($"{SAVE_KEY}_EquipAttack", equipmentBonus.attackBonus);
        PlayerPrefs.SetInt($"{SAVE_KEY}_EquipDefense", equipmentBonus.defenseBonus);
        PlayerPrefs.SetInt($"{SAVE_KEY}_EquipSpeed", equipmentBonus.speedBonus);
        
        PlayerPrefs.Save();
    }
    
    void LoadStats()
    {
        currentLevel = PlayerPrefs.GetInt($"{SAVE_KEY}_Level", 1);
        currentXP = PlayerPrefs.GetInt($"{SAVE_KEY}_XP", 0);
        xpToNextLevel = PlayerPrefs.GetInt($"{SAVE_KEY}_XPNext", 100);
        
        baseStats.hp = PlayerPrefs.GetInt($"{SAVE_KEY}_BaseHP", 100);
        baseStats.mp = PlayerPrefs.GetInt($"{SAVE_KEY}_BaseMP", 50);
        baseStats.attack = PlayerPrefs.GetInt($"{SAVE_KEY}_BaseAttack", 20);
        baseStats.defense = PlayerPrefs.GetInt($"{SAVE_KEY}_BaseDefense", 10);
        baseStats.speed = PlayerPrefs.GetInt($"{SAVE_KEY}_BaseSpeed", 15);
        
        equipmentBonus.hpBonus = PlayerPrefs.GetInt($"{SAVE_KEY}_EquipHP", 0);
        equipmentBonus.mpBonus = PlayerPrefs.GetInt($"{SAVE_KEY}_EquipMP", 0);
        equipmentBonus.attackBonus = PlayerPrefs.GetInt($"{SAVE_KEY}_EquipAttack", 0);
        equipmentBonus.defenseBonus = PlayerPrefs.GetInt($"{SAVE_KEY}_EquipDefense", 0);
        equipmentBonus.speedBonus = PlayerPrefs.GetInt($"{SAVE_KEY}_EquipSpeed", 0);
    }
}
```

**Setup Instructions:**

1. **Create UI Elements:**
   - Create a Canvas with Text elements for:
     - Level display
     - XP display
     - HP display
     - MP display
     - Attack display
     - Defense display
     - Speed display

2. **Attach Script:**
   - Attach the `CharacterStats` script to a GameObject in your scene

3. **Assign UI References:**
   - In the Inspector, drag your UI Text elements to the corresponding fields in the script

4. **Equipment Bonuses:**
   - Create `EquipmentBonus` objects in other scripts and call:
     ```csharp
     characterStats.AddEquipmentBonus(equipmentBonus);
     characterStats.RemoveEquipmentBonus(equipmentBonus);
     ```

5. **Adding XP:**
   - Call `AddXP(amount)` to grant experience points

**Key Features:**

- **Base Stats:** Configurable in Inspector
- **Level System:** Automatically levels up when XP threshold is reached
- **XP Progression:** Increases by 50% each level
- **Stat Calculation:** Combines base stats with equipment bonuses
- **Level Rewards:** Stat increases on level up
- **Persistence:** Saves all stats using PlayerPrefs
- **UI Updates:** Automatically updates UI when stats change
- **Equipment Management:** Add/remove equipment bonuses

**Example Usage:**
```csharp
// Grant XP
characterStats.AddXP(150);

// Add equipment bonus
EquipmentBonus swordBonus = new EquipmentBonus { attackBonus = 10, speedBonus = 2 };
characterStats.AddEquipmentBonus(swordBonus);
```

This implementation provides a complete character stats system with all requested features. The system automatically handles stat calculations, level progression, UI updates, and data persistence.