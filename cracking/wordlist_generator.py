"""
Cerbero Engine - Advanced Wordlist Generator
Integrated into WifiBreaker Pro
"""

import itertools
from datetime import datetime
from typing import List, Dict, Set


class CerberoEngine:
    """
    Motor avanzado de generación de wordlists basado en información personal.
    Implementa 6 motores especializados de generación.
    """
    
    LEETSPEAK_MAP = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7']
    }
    
    def __init__(self):
        self.passwords = set()
    
    def full_leetspeak(self, text: str) -> str:
        """Convierte texto completo a leetspeak."""
        text = text.lower()
        for char, replacements in self.LEETSPEAK_MAP.items():
            if replacements:
                text = text.replace(char, replacements[0])
        return text
    
    def apply_variations(self, word: str) -> List[str]:
        """Aplica variaciones de mayúsculas/minúsculas."""
        word = word.lower()
        return list(set([word, word.capitalize(), word.upper()]))
    
    def apply_mangling_rules(self, word: str) -> List[str]:
        """Aplica reglas de mangling (leetspeak parcial y completo)."""
        word = word.lower()
        results = {word, word.upper(), word.capitalize()}
        
        # Leetspeak completo para palabras largas
        if len(word) > 7:
            leet_word = self.full_leetspeak(word)
            results.update([leet_word, leet_word.capitalize(), leet_word.upper()])
            return list(results)
        
        # Leetspeak parcial (combinaciones)
        chars_to_replace = [(i, char) for i, char in enumerate(word) if char in self.LEETSPEAK_MAP]
        
        for i in range(1, len(chars_to_replace) + 1):
            for positions_combo in itertools.combinations(chars_to_replace, i):
                indices = [p[0] for p in positions_combo]
                possible_replacements = [self.LEETSPEAK_MAP[p[1]] for p in positions_combo]
                
                for replacement_values in itertools.product(*possible_replacements):
                    temp_word = list(word)
                    for j, index in enumerate(indices):
                        temp_word[index] = replacement_values[j]
                    mangled_word = "".join(temp_word)
                    results.update([mangled_word, mangled_word.capitalize(), mangled_word.upper()])
        
        return list(results)
    
    def extract_base_words(self, info: Dict) -> List[str]:
        """Extrae todas las palabras base de la información."""
        words = set()
        
        def extract(data):
            if isinstance(data, dict):
                for value in data.values():
                    extract(value)
            elif isinstance(data, list):
                for item in data:
                    extract(item)
            elif isinstance(data, str) and data:
                cleaned = data.strip()
                if cleaned:
                    for word in cleaned.lower().split():
                        words.add(word)
        
        extract(info)
        return list(filter(None, words))
    
    def motor_1_simple_combinations(self, text_words: List[str], numeric_words: List[str]) -> Set[str]:
        """Motor 1: Combinaciones simples (estilo RockYou)."""
        passwords = set()
        
        # Variaciones individuales
        for text in text_words:
            for var in self.apply_variations(text):
                passwords.add(var)
                # Con números
                for num in numeric_words:
                    passwords.add(f"{var}{num}")
        
        # Permutaciones de 2 palabras
        for w1, w2 in itertools.permutations(text_words, 2):
            for var1 in self.apply_variations(w1):
                for var2 in self.apply_variations(w2):
                    passwords.add(f"{var1}{var2}")
        
        return passwords
    
    def motor_2_complex_patterns(self, text_words: List[str], numeric_words: List[str]) -> Set[str]:
        """Motor 2: Patrones complejos (estilo WiFi)."""
        passwords = set()
        separators = ['-', '_', '.', '']
        symbols_pre_num = ['/', '-', '_', '#', '@']
        
        for w1, w2 in itertools.permutations(text_words, 2):
            for var1 in self.apply_variations(w1):
                for var2 in self.apply_variations(w2):
                    for sep in separators:
                        base = f"{var1}{sep}{var2}"
                        passwords.add(base)
                        
                        # Con números y símbolos
                        for num in numeric_words:
                            for sym in symbols_pre_num:
                                passwords.add(f"{base}{sym}{num}")
        
        return passwords
    
    def motor_3_modern_leetspeak(self, info: Dict) -> Set[str]:
        """Motor 3: Patrones modernos con leetspeak (2025D4n13l%)."""
        passwords = set()
        current_year = str(datetime.now().year)
        symbols = ['$', '#', '!', '*', '.', '&', '%', '@']
        
        # Nombres principales
        names = {n.lower() for n in info["persona_principal"]["nombres"] if n}
        if info["persona_principal"].get("sobrenombre"):
            names.add(info["persona_principal"]["sobrenombre"].lower())
        
        for name in names:
            if len(name) > 1:
                # Patrón: Primera mayúscula + resto leetspeak
                leet_base = f"{name[0].upper()}{self.full_leetspeak(name[1:])}"
                
                for sym in symbols:
                    passwords.add(f"{current_year}{leet_base}{sym}")
                    passwords.add(f"{leet_base}{current_year}{sym}")
        
        return passwords
    
    def motor_4_children_patterns(self, info: Dict) -> Set[str]:
        """Motor 4: Patrones centrados en hijos (2014Jiub$)."""
        passwords = set()
        symbols = ['$', '#', '!', '*', '.', '&', '%', '@']
        
        for hijo in info.get("familia", {}).get("hijos", []):
            if hijo.get("fecha_nacimiento") and hijo.get("nombres"):
                year = str(hijo["fecha_nacimiento"].year)
                
                # Iniciales de nombres y apellidos
                initials = "".join([n[0] for n in hijo["nombres"] if n] + 
                                 [a[0] for a in hijo.get("apellidos", []) if a]).lower()
                
                if initials:
                    initials_cased = initials.capitalize()
                    
                    for sym in symbols:
                        passwords.add(f"{year}{initials_cased}{sym}")
                        passwords.add(f"{initials_cased}{year}{sym}")
        
        return passwords
    
    def motor_5_initials_permutations(self, info: Dict) -> Set[str]:
        """Motor 5: Permutación de iniciales (Cdck1277kd)."""
        passwords = set()
        
        # Recopilar todas las iniciales
        all_initials = []
        all_initials.extend([n[0] for n in info.get("persona_principal", {}).get("nombres", []) if n])
        all_initials.extend([n[0] for n in info.get("familia", {}).get("pareja", {}).get("nombres", []) if n])
        
        for hijo in info.get("familia", {}).get("hijos", []):
            all_initials.extend([n[0] for n in hijo.get("nombres", []) if n])
        
        # Números clave de fechas
        key_numbers = set()
        all_dates = [
            info.get("persona_principal", {}).get("fecha_nacimiento"),
            info.get("familia", {}).get("pareja", {}).get("fecha_nacimiento")
        ] + [h.get("fecha_nacimiento") for h in info.get("familia", {}).get("hijos", [])]
        
        for f_nac in filter(None, all_dates):
            key_numbers.update([f"{f_nac.day:02d}", str(f_nac.year)[2:]])
        
        # Generar permutaciones
        if len(all_initials) >= 2 and len(key_numbers) >= 2:
            for i in range(3, min(len(all_initials) + 1, 6)):
                for p_initials in itertools.permutations(all_initials, i):
                    initial_part = "".join(p_initials)
                    initial_part_cased = initial_part[0].upper() + initial_part[1:].lower()
                    
                    for p_numbers in itertools.permutations(key_numbers, 2):
                        number_part = "".join(p_numbers)
                        passwords.add(f"{initial_part_cased}{number_part}")
                        
                        # Con iniciales restantes
                        remaining = all_initials[:]
                        for char in p_initials:
                            if char in remaining:
                                remaining.remove(char)
                        
                        if len(remaining) >= 2:
                            for p_rem in itertools.permutations(remaining, 2):
                                passwords.add(f"{initial_part_cased}{number_part}{''.join(p_rem).lower()}")
        
        return passwords
    
    def motor_6_phrase_mangler(self, info: Dict) -> Set[str]:
        """Motor 6: Mangler de frases (R3d$S3gura2024!#)."""
        passwords = set()
        
        mangle_phrases = [p for p in info.get("otros_datos", {}).get("mangle_phrases", []) if p]
        
        if not mangle_phrases:
            return passwords
        
        years = {str(datetime.now().year)}
        if info.get("persona_principal", {}).get("fecha_nacimiento"):
            years.add(str(info["persona_principal"]["fecha_nacimiento"].year))
        
        complex_suffixes = ["!", "#", "!#", "@#", "!!", "*"]
        
        for phrase in mangle_phrases:
            words = phrase.strip().split()
            
            if len(words) == 2:
                w1, w2 = words
                mangled1_list = self.apply_mangling_rules(w1)
                mangled2_list = self.apply_mangling_rules(w2)
                
                for m1 in mangled1_list:
                    for m2 in mangled2_list:
                        base = f"{m1}{m2}"
                        passwords.add(base)
                        
                        # Con años
                        for year in years:
                            pass_year = f"{base}{year}"
                            passwords.add(pass_year)
                            
                            # Con sufijos complejos
                            for suffix in complex_suffixes:
                                passwords.add(f"{pass_year}{suffix}")
        
        return passwords
    
    def generate_full_passwords(self, info: Dict, min_length: int = 8, max_length: int = 16) -> List[str]:
        """
        Genera contraseñas usando los 6 motores y filtra por longitud.
        
        Args:
            info: Diccionario con información personal
            min_length: Longitud mínima de contraseña
            max_length: Longitud máxima de contraseña
        
        Returns:
            Lista de contraseñas generadas
        """
        self.passwords = set()
        
        # Extraer palabras base
        base_words = self.extract_base_words(info)
        text_words = [w for w in base_words if not w.isdigit()]
        numeric_words = [w for w in base_words if w.isdigit()]
        
        print(f"  [*] Palabras base encontradas: {len(base_words)}")
        print(f"      Texto: {len(text_words)} | Números: {len(numeric_words)}")
        
        # Ejecutar motores
        print("\n  [Motor 1] Combinaciones simples...")
        self.passwords.update(self.motor_1_simple_combinations(text_words, numeric_words))
        print(f"      Generadas: {len(self.passwords):,}")
        
        print("  [Motor 2] Patrones complejos...")
        initial_count = len(self.passwords)
        self.passwords.update(self.motor_2_complex_patterns(text_words, numeric_words))
        print(f"      Nuevas: {len(self.passwords) - initial_count:,}")
        
        print("  [Motor 3] Leetspeak moderno...")
        initial_count = len(self.passwords)
        self.passwords.update(self.motor_3_modern_leetspeak(info))
        print(f"      Nuevas: {len(self.passwords) - initial_count:,}")
        
        print("  [Motor 4] Patrones de hijos...")
        initial_count = len(self.passwords)
        self.passwords.update(self.motor_4_children_patterns(info))
        print(f"      Nuevas: {len(self.passwords) - initial_count:,}")
        
        print("  [Motor 5] Permutación de iniciales...")
        initial_count = len(self.passwords)
        self.passwords.update(self.motor_5_initials_permutations(info))
        print(f"      Nuevas: {len(self.passwords) - initial_count:,}")
        
        print("  [Motor 6] Mangler de frases...")
        initial_count = len(self.passwords)
        self.passwords.update(self.motor_6_phrase_mangler(info))
        print(f"      Nuevas: {len(self.passwords) - initial_count:,}")
        
        print(f"\n  [*] Total generadas: {len(self.passwords):,}")
        
        # Filtrar por longitud
        filtered = [p for p in self.passwords if min_length <= len(p) <= max_length]
        print(f"  [*] Después de filtrar ({min_length}-{max_length} chars): {len(filtered):,}")
        
        return filtered