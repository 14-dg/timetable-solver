from mock_data.generate import MockGenerator


def main():
    mock_generator = MockGenerator()

    mock_lectures, mock_rooms, mock_teachers = mock_generator.generate_mock_data()
        
    print("--- Beispiel Teacher ---")
    print(mock_teachers[0])
    
    print("\n--- Beispiel Room ---")
    print(mock_rooms[0])

    print("--- Beispiel Lecture ---")
    print(mock_lectures[0])


if __name__ == "__main__":
    main()