lab2_ardupilot/
├── scripts/
│   └── start.sh                      скрипт автоматичного запуску симуляції
└── src/fpv_lab2/
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── LICENSE
    ├── resource/fpv_lab2
    ├── test/
    └── fpv_lab2/
        ├── __init__.py
        ├── main.py
        ├── flight_state.py           [MOD] додано стан MOVING_TO_TARGET
        ├── flight_test_node.py       [MOD] додано нові константи, новий публікатор, 
                                        def publish_velocity, def odometry_callback
        └── handlers/
            ├── __init__.py           [MOD] зареєстровано MovingToTargetHandler у HANDLERS
            ├── handler.py
            ├── waiting_for_system.py
            ├── prearm_check.py
            ├── setting_guided.py
            ├── arming.py
            ├── taking_off.py
            ├── hovering.py           [MOD] після зависання веде в MOVING_TO_TARGET
            ├── moving_to_target.py   [NEW] політ до цілі
            ├── landing.py
            └── waiting_for_landing.py