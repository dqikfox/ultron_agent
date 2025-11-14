// Simple RPG System for ULTRON Avatars (Kid-Friendly)

const DND = {
    classes: {
        warrior: { name: '⚔️ Warrior', hp: 20, power: 'Smash Attack', emoji: '⚔️' },
        mage: { name: '🔮 Mage', hp: 12, power: 'Fireball', emoji: '🔮' },
        rogue: { name: '🗡️ Rogue', hp: 15, power: 'Sneak Attack', emoji: '🗡️' },
        healer: { name: '✨ Healer', hp: 14, power: 'Heal Spell', emoji: '✨' },
        ranger: { name: '🏹 Ranger', hp: 16, power: 'Arrow Shot', emoji: '🏹' },
        necromancer: { name: '💀 Necromancer', hp: 13, power: 'Summon Undead', emoji: '💀' },
        berserker: { name: '🪓 Berserker', hp: 22, power: 'Rage Mode', emoji: '🪓' },
        assassin: { name: '🔪 Assassin', hp: 14, power: 'Backstab', emoji: '🔪' }
    },
    
    races: {
        elf: { name: '🧝 Elf', bonus: '+2 Speed', special: 'Forest Magic' },
        dwarf: { name: '⛏️ Dwarf', bonus: '+3 Defense', special: 'Stone Skin' },
        orc: { name: '👹 Orc', bonus: '+4 Strength', special: 'Battle Rage' },
        demon: { name: '😈 Demon', bonus: '+3 Dark Magic', special: 'Soul Drain' },
        vampire: { name: '🧛 Vampire', bonus: '+2 Life Steal', special: 'Blood Frenzy' },
        dragon: { name: '🐉 Dragon', bonus: '+5 Fire Breath', special: 'Dragon Wings' },
        zombie: { name: '🧟 Zombie', bonus: '+4 Undead', special: 'Cannot Die Easily' },
        robot: { name: '🤖 Robot', bonus: '+3 Tech', special: 'Self Repair' }
    },
    
    alignments: ['😇 Hero', '😐 Neutral', '😈 Villain', '🤪 Chaotic', '💀 Evil'],
    
    weapons: ['Sword', 'Axe', 'Bow', 'Staff', 'Dagger', 'Hammer', 'Scythe', 'Claws'],
    armor: ['Leather', 'Chain Mail', 'Plate Armor', 'Robes', 'Dragon Scale'],
    items: ['Health Potion', 'Mana Potion', 'Bomb', 'Rope', 'Torch', 'Magic Ring', 'Shield'],
    
    rollDice(sides = 20) {
        return Math.floor(Math.random() * sides) + 1;
    },
    
    createCharacter(className, raceName) {
        const charClass = this.classes[className];
        const race = this.races[raceName];
        const alignment = this.alignments[Math.floor(Math.random() * this.alignments.length)];
        
        const attack = this.rollDice(10);
        const defense = this.rollDice(10);
        const magic = this.rollDice(10);
        const speed = this.rollDice(10);
        
        const weapon = this.weapons[Math.floor(Math.random() * this.weapons.length)];
        const armorPiece = this.armor[Math.floor(Math.random() * this.armor.length)];
        const startItems = [];
        for (let i = 0; i < 3; i++) {
            startItems.push(this.items[Math.floor(Math.random() * this.items.length)]);
        }
        
        return {
            class: charClass.name,
            classEmoji: charClass.emoji,
            race: race.name,
            level: 1,
            alignment: alignment,
            hp: charClass.hp,
            maxHp: charClass.hp,
            attack: attack,
            defense: defense,
            magic: magic,
            speed: speed,
            power: charClass.power,
            special: race.special,
            bonus: race.bonus,
            weapon: weapon,
            armor: armorPiece,
            inventory: [weapon, armorPiece, ...startItems],
            gold: this.rollDice(100),
            kills: 0,
            victories: 0
        };
    },
    
    attack(attacker, defender) {
        const roll = this.rollDice(20);
        const damage = attacker.attack + roll;
        const blocked = defender.defense;
        const finalDamage = Math.max(1, damage - blocked);
        
        defender.hp -= finalDamage;
        
        return {
            hit: roll > 5,
            damage: finalDamage,
            critical: roll === 20,
            miss: roll === 1,
            killed: defender.hp <= 0
        };
    }
};
