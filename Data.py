#!/usr/bin/env python3
import Sim_Data

if __name__ == "__main__":
    try:
        Sim_Data.main()
    except KeyboardInterrupt:
        print("\nExiting...")