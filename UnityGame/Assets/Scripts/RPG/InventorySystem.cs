Here's a complete Unity C# inventory system implementation with all requested features:

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;

// Item Types
public enum ItemType
{
    Weapon,
    Armor,
    Accessory,
    Consumable,
    Material
}

// Item Data Structure
[Serializable]
public class ItemData
{
    public int id;
    public string name;
    public ItemType type;
    public int maxStack = 1;
    public Dictionary<string, int> stats = new Dictionary<string, int>();

    public ItemData(int id, string name, ItemType type, int maxStack = 1)
    {
        this.id = id;
        this.name = name;
        this.type = type;
        this.maxStack = maxStack;
    }

    public ItemData(ItemData other)
    {
        id = other.id;
        name = other.name;
        type = other.type;
        maxStack = other.maxStack;
        stats = new Dictionary<string, int>(other.stats);
    }
}

// Inventory Item (with quantity for stacking)
[Serializable]
public class InventoryItem
{
    public ItemData itemData;
    public int quantity;

    public InventoryItem(ItemData data, int quantity = 1)
    {
        itemData = new ItemData(data);
        this.quantity = quantity;
    }

    public bool IsStackable()
    {
        return itemData.maxStack > 1;
    }
}

// Equipment Slots
public enum EquipmentSlot
{
    Weapon,
    Helmet,
    Chest,
    Legs,
    Accessory1,
    Accessory2
}

// Main Inventory System
public class InventorySystem : MonoBehaviour
{
    [Header("Inventory Settings")]
    public int inventoryCapacity = 20;
    
    [Header("Equipment")]
    public Dictionary<EquipmentSlot, InventoryItem> equipment = new Dictionary<EquipmentSlot, InventoryItem>();
    
    [Header("Inventory")]
    public List<InventoryItem> items = new List<InventoryItem>();
    
    // Events
    public Action<InventoryItem> onItemAdded;
    public Action<InventoryItem> onItemRemoved;
    public Action<EquipmentSlot, InventoryItem> onItemEquipped;
    public Action<EquipmentSlot> onItemUnequipped;

    void Start()
    {
        InitializeEquipment();
    }

    void InitializeEquipment()
    {
        foreach (EquipmentSlot slot in Enum.GetValues(typeof(EquipmentSlot)))
        {
            equipment[slot] = null;
        }
    }

    // Add item to inventory
    public bool AddItem(ItemData itemData, int quantity = 1)
    {
        if (itemData == null || quantity <= 0) return false;

        // Try to stack with existing items first
        if (itemData.maxStack > 1)
        {
            for (int i = 0; i < items.Count; i++)
            {
                if (items[i].itemData.id == itemData.id && 
                    items[i].quantity < items[i].itemData.maxStack)
                {
                    int spaceLeft = items[i].itemData.maxStack - items[i].quantity;
                    int amountToAdd = Mathf.Min(quantity, spaceLeft);
                    
                    items[i].quantity += amountToAdd;
                    quantity -= amountToAdd;
                    
                    onItemAdded?.Invoke(items[i]);
                    
                    if (quantity <= 0) return true;
                }
            }
        }

        // Add new stack if there's still quantity left
        while (quantity > 0 && items.Count < inventoryCapacity)
        {
            int stackSize = itemData.maxStack > 1 ? 
                Mathf.Min(quantity, itemData.maxStack) : 1;
            
            InventoryItem newItem = new InventoryItem(itemData, stackSize);
            items.Add(newItem);
            onItemAdded?.Invoke(newItem);
            
            quantity -= stackSize;
        }

        return quantity <= 0;
    }

    // Remove item from inventory
    public bool RemoveItem(int itemId, int quantity = 1)
    {
        if (quantity <= 0) return false;

        for (int i = items.Count - 1; i >= 0; i--)
        {
            if (items[i].itemData.id == itemId)
            {
                if (items[i].quantity > quantity)
                {
                    items[i].quantity -= quantity;
                    onItemRemoved?.Invoke(items[i]);
                    return true;
                }
                else
                {
                    quantity -= items[i].quantity;
                    onItemRemoved?.Invoke(items[i]);
                    items.RemoveAt(i);
                }

                if (quantity <= 0) return true;
            }
        }

        return false;
    }

    // Use item (for consumables)
    public bool UseItem(int index)
    {
        if (index < 0 || index >= items.Count) return false;

        InventoryItem item = items[index];
        
        // Only consumables can be used
        if (item.itemData.type != ItemType.Consumable) return false;

        // Apply item effect here (custom implementation needed)
        Debug.Log($"Used {item.itemData.name}");

        // Remove one quantity
        if (item.quantity > 1)
        {
            item.quantity--;
            onItemRemoved?.Invoke(item);
        }
        else
        {
            items.RemoveAt(index);
            onItemRemoved?.Invoke(item);
        }

        return true;
    }

    // Equip item
    public bool EquipItem(int index)
    {
        if (index < 0 || index >= items.Count) return false;

        InventoryItem item = items[index];
        EquipmentSlot slot = GetEquipmentSlotForItem(item.itemData.type);

        if (slot == EquipmentSlot.Weapon && item.itemData.type != ItemType.Weapon)
            return false;
        if ((slot == EquipmentSlot.Helmet || slot == EquipmentSlot.Chest || slot == EquipmentSlot.Legs) 
            && item.itemData.type != ItemType.Armor)
            return false;
        if ((slot == EquipmentSlot.Accessory1 || slot == EquipmentSlot.Accessory2) 
            && item.itemData.type != ItemType.Accessory)
            return false;

        // Unequip current item in slot if exists
        if (equipment[slot] != null)
        {
            AddItem(equipment[slot].itemData, equipment[slot].quantity);
        }

        // Equip new item
        equipment[slot] = new InventoryItem(item.itemData, item.quantity);
        onItemEquipped?.Invoke(slot, equipment[slot]);

        // Remove from inventory
        items.RemoveAt(index);
        onItemRemoved?.Invoke(item);

        return true;
    }

    // Unequip item
    public bool UnequipItem(EquipmentSlot slot)
    {
        if (equipment[slot] == null) return false;

        // Add back to inventory
        if (!AddItem(equipment[slot].itemData, equipment[slot].quantity))
        {
            Debug.LogWarning("Not enough inventory space to unequip item");
            return false;
        }

        // Remove from equipment
        equipment[slot] = null;
        onItemUnequipped?.Invoke(slot);

        return true;
    }

    // Get appropriate equipment slot for item type
    EquipmentSlot GetEquipmentSlotForItem(ItemType type)
    {
        switch (type)
        {
            case ItemType.Weapon: return EquipmentSlot.Weapon;
            case ItemType.Armor:
                // This would need more specific armor types in a real implementation
                return EquipmentSlot.Chest;
            case ItemType.Accessory: 
                // Find first available accessory slot
                return equipment[EquipmentSlot.Accessory1] == null ? 
                    EquipmentSlot.Accessory1 : EquipmentSlot.Accessory2;
            default: return EquipmentSlot.Weapon;
        }
    }

    // Get item count
    public int GetItemCount(int itemId)
    {
        int count = 0;
        foreach (var item in items)
        {
            if (item.itemData.id == itemId)
                count += item.quantity;
        }
        return count;
    }

    // Check if inventory is full
    public bool IsFull()
    {
        return items.Count >= inventoryCapacity;
    }
}
```

**Inventory UI Implementation:**

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class InventoryUI : MonoBehaviour
{
    [Header("UI References")]
    public GameObject inventoryPanel;
    public Transform itemContainer;
    public GameObject itemSlotPrefab;
    
    [Header("Equipment UI")]
    public Dictionary<EquipmentSlot, Image> equipmentSlots = new Dictionary<EquipmentSlot, Image>();
    public GameObject equipmentPanel;

    private InventorySystem inventory;
    private List<ItemSlotUI> itemSlots = new List<ItemSlotUI>();

    void Start()
    {
        inventory = FindObjectOfType<InventorySystem>();
        if (inventory == null)
        {
            Debug.LogError("InventorySystem not found in scene!");
            return;
        }

        InitializeUI();
        inventory.onItemAdded += RefreshUI;
        inventory.onItemRemoved += RefreshUI;
        inventory.onItemEquipped += OnItemEquipped;
        inventory.onItemUnequipped += OnItemUnequipped;
    }

    void InitializeUI()
    {
        // Create item slots
        for (int i = 0; i < inventory.inventoryCapacity; i++)
        {
            GameObject slotObj = Instantiate(itemSlotPrefab, itemContainer);
            ItemSlotUI slotUI = slotObj.GetComponent<ItemSlotUI>();
            slotUI.Setup(i, this);
            itemSlots.Add(slotUI);
        }

        // Setup equipment slots (you would assign these in inspector)
        // Example: equipmentSlots[EquipmentSlot.Weapon] = weaponSlotImage;
        
        RefreshUI();
    }

    public void RefreshUI()
    {
        // Update inventory slots
        for (int i = 0; i < itemSlots.Count; i++)
        {
            if (i < inventory.items.Count)
            {
                itemSlots[i].SetItem(inventory.items[i]);
            }
            else
            {
                itemSlots[i].Clear();
            }
        }

        // Update equipment slots
        foreach (var slot in inventory.equipment)
        {
            if (equipmentSlots.ContainsKey(slot.Key) && slot.Value != null)
            {
                // Update equipment slot UI
                // equipmentSlots[slot.Key].sprite = GetItemIcon(slot.Value.itemData);
            }
        }
    }

    void OnItemEquipped(EquipmentSlot slot, InventoryItem item)
    {
        RefreshUI();
    }

    void OnItemUnequipped(EquipmentSlot slot)
    {
        RefreshUI();
    }

    public void ToggleInventory()
    {
        inventoryPanel.SetActive(!inventoryPanel.activeSelf);
        if (inventoryPanel.activeSelf)
        {
            RefreshUI();
        }
    }

    // Called by UI buttons
    public void OnItemSlotClick(int index)
    {
        if (index < inventory.items.Count)
        {
            // Show item options (use, equip, etc.)
            if (inventory.items[index].itemData.type == ItemType.Consumable)
            {
                inventory.UseItem(index);
            }
            else
            {
                inventory.EquipItem(index);
            }
        }
    }
}
```

**Item Slot UI Component:**

```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ItemSlotUI : MonoBehaviour
{
    [Header("UI Components")]
    public Image icon;
    public TextMeshProUGUI quantityText;
    public Button slotButton;
    
    private int slotIndex;
    private InventoryUI inventoryUI;
    private InventoryItem item;

    public void Setup(int index, InventoryUI ui)
    {
        slotIndex = index;
        inventoryUI = ui;
        slotButton.onClick.AddListener(() => inventoryUI.OnItemSlotClick(slotIndex));
        Clear();
    }

    public void SetItem(InventoryItem inventoryItem)
    {
        item = inventoryItem;
        icon.gameObject.SetActive(true);
        icon.sprite = GetItemIcon(inventoryItem.itemData); // Implement this method
        
        if (inventoryItem.quantity > 1)
        {
            quantityText.text = inventoryItem.quantity.ToString();
            quantityText.gameObject.SetActive(true);
        }
        else
        {
            quantityText.gameObject.SetActive(false);
        }
    }

    public void Clear()
    {
        item = null;
        icon.gameObject.SetActive(false);
        quantityText.gameObject.SetActive(false);
    }

    Sprite GetItemIcon(ItemData itemData)
    {
        // Return appropriate sprite based on item
        // This is a placeholder - implement based on your assets
        return null;
    }
}
```

**Usage Instructions:**

1. **Setup:**
   - Attach `InventorySystem` to a GameObject
   - Create UI elements and attach `InventoryUI`
   - Create item slot prefabs with `ItemSlotUI` component

2. **Adding Items:**
   ```csharp
   ItemData sword = new ItemData(1, "Iron Sword", ItemType.Weapon);
   sword.stats["damage"] = 10;
   inventory.AddItem(sword);
   ```

3. **Creating Stackable Items:**
   ```csharp
   ItemData potion = new ItemData(2, "Health Potion", ItemType.Consumable, 10);
   inventory.AddItem(potion, 5); // Adds 5 potions to a stack
   ```

4. **Key Features Implemented:**
   - Full item data structure with ID, name, type, and stats
   - Configurable inventory capacity
   - Stackable items with automatic stacking
   - Equipment system with multiple slot types
   - Add/remove/use item functionality
   - Event-driven UI updates
   - Modular UI components

This implementation provides a complete foundation that can be extended with:
- Item rarity systems
- Tooltip displays
- Drag-and-drop functionality
- Save/load systems
- Advanced equipment slot management
- Item database serialization