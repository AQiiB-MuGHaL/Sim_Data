import sys

if __name__ == "__main__":
    try:
        # Seedha apni Cythonize ki hui file ko import karein
        import Fresh_Data
        
        # Check karein ke file ke andar konsa main function run hone ke liye hai
        if hasattr(Fresh_Data, 'main'):
            Fresh_Data.main()
        elif hasattr(Fresh_Data, 'main_menu'):
            Fresh_Data.main_menu()
        else:
            print("Module successfully loaded!")
            
    except Exception as e:
        print(f"Error: {e}")
