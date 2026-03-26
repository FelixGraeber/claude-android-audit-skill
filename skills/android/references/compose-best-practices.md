# Jetpack Compose Performance & Patterns

## Stability & Recomposition

### @Immutable and @Stable

The Compose compiler determines whether parameters are "stable" to decide if a composable can be skipped during recomposition.

**Stable by default:** primitives, `String`, function types (lambdas), `enum` classes, data classes where all properties are stable.

**Unstable by default:** `List`, `Set`, `Map` (standard Kotlin collections), classes with `var` properties, classes from external modules without Compose compiler.

```kotlin
// Mark as immutable -- compiler trusts this will never change
@Immutable
data class UiModel(
    val id: String,
    val title: String,
    val items: List<Item>  // List is unstable, but @Immutable overrides
)

// Mark as stable -- compiler trusts equals() is correct and changes notify composition
@Stable
class FormState(
    val name: MutableStateFlow<String>,
    val email: MutableStateFlow<String>
)
```

### Strong Skipping Mode

Default since Kotlin 2.0.20+ / Compose Compiler 1.5.4+. Changes:
- Lambdas with unstable captures are **automatically remembered**
- Composables with unstable parameters can be skipped if instances are **referentially equal** (`===`)
- Reduces need for manual `@Stable`/`@Immutable` annotations

Verify it is enabled:

```kotlin
// build.gradle.kts
composeCompiler {
    featureFlags = setOf(ComposeFeatureFlag.StrongSkipping) // already default
}
```

### Kotlin Immutable Collections

Use `kotlinx-collections-immutable` for stable collection types:

```kotlin
// Stable -- Compose compiler recognizes these
val items: ImmutableList<Item> = persistentListOf()
val map: ImmutableMap<String, Int> = persistentMapOf()
```

---

## State Management

### derivedStateOf

Use when a state value is computed from other state values and you want to avoid unnecessary recompositions:

```kotlin
// Good: only recomposes when the derived value actually changes
val showButton by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

// Bad: recomposes on every scroll pixel
val showButton = listState.firstVisibleItemIndex > 0
```

### collectAsStateWithLifecycle vs collectAsState

Always prefer `collectAsStateWithLifecycle` in Android UI:

```kotlin
// Correct: stops collecting when lifecycle is below STARTED
val uiState by viewModel.uiState.collectAsStateWithLifecycle()

// Wrong: keeps collecting even when app is backgrounded (wasted resources, crashes)
val uiState by viewModel.uiState.collectAsState()
```

### rememberSaveable

Use for UI state that must survive configuration changes and process death:

```kotlin
var text by rememberSaveable { mutableStateOf("") }
var expanded by rememberSaveable { mutableStateOf(false) }

// Custom saver for complex objects
val state = rememberSaveable(saver = MyState.Saver) { MyState() }
```

### ViewModel + StateFlow (MVI)

```kotlin
class ScreenViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(ScreenUiState())
    val uiState: StateFlow<ScreenUiState> = _uiState.asStateFlow()

    fun onEvent(event: ScreenEvent) {
        when (event) {
            is ScreenEvent.Search -> search(event.query)
            is ScreenEvent.Select -> select(event.id)
        }
    }

    private fun search(query: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val results = repository.search(query)
            _uiState.update { it.copy(isLoading = false, results = results) }
        }
    }
}

@Immutable
data class ScreenUiState(
    val isLoading: Boolean = false,
    val results: ImmutableList<Result> = persistentListOf(),
    val error: String? = null
)

sealed interface ScreenEvent {
    data class Search(val query: String) : ScreenEvent
    data class Select(val id: String) : ScreenEvent
}
```

---

## Performance Patterns

### Lambda-Based Modifiers for Animations

Deferred reads prevent recomposition on every animation frame:

```kotlin
// Good: reads offset during draw phase only, no recomposition
Box(
    Modifier.graphicsLayer {
        translationY = offset.value
        alpha = alpha.value
    }
)

// Bad: recomposes on every frame
Box(
    Modifier
        .offset(y = offset.value.dp)
        .alpha(alpha.value)
)
```

### Deferred State Reads

Push state reads as deep as possible:

```kotlin
// Good: only Text recomposes when name changes
@Composable
fun UserCard(nameProvider: () -> String) {
    Card {
        Text(nameProvider())
    }
}

// Bad: entire UserCard recomposes when name changes
@Composable
fun UserCard(name: String) {
    Card {
        Text(name)
    }
}
```

### Avoid Backwards Writes

Never write to state that was already read during the current composition:

```kotlin
// BAD: backwards write causes infinite recomposition loop
var count by remember { mutableIntStateOf(0) }
Text("$count")
count++  // writing after reading -- NEVER do this

// OK: write in response to events
Button(onClick = { count++ }) { Text("$count") }
```

### LazyColumn Performance

```kotlin
LazyColumn {
    items(
        items = list,
        key = { it.id },             // stable keys for item reuse
        contentType = { it.type }     // type hints for view recycling
    ) { item ->
        ItemRow(item)
    }
}
```

- Always provide `key` -- without it, items are keyed by index (breaks animations, loses state)
- Provide `contentType` when items have different layouts (helps prefetching)
- Avoid `items(list.size) { index -> list[index] }` pattern -- use `items(list)`

### key() for Non-Lazy Compositions

```kotlin
// Force recomposition when id changes (reset internal state)
key(user.id) {
    UserProfile(user)
}
```

---

## Side Effects

### LaunchedEffect

Runs a suspend function scoped to the composition. Cancels and relaunches when keys change.

```kotlin
// Load data when screen appears or id changes
LaunchedEffect(userId) {
    viewModel.loadUser(userId)
}

// One-time effect
LaunchedEffect(Unit) {
    analytics.trackScreenView("Home")
}
```

### DisposableEffect

For effects that need cleanup:

```kotlin
DisposableEffect(lifecycleOwner) {
    val observer = LifecycleEventObserver { _, event ->
        if (event == Lifecycle.Event.ON_RESUME) { /* ... */ }
    }
    lifecycleOwner.lifecycle.addObserver(observer)
    onDispose {
        lifecycleOwner.lifecycle.removeObserver(observer)
    }
}
```

### SideEffect

Runs after every successful composition. Use to publish Compose state to non-Compose code:

```kotlin
SideEffect {
    analytics.setUserProperty("theme", if (isDark) "dark" else "light")
}
```

### Rules

- Never call `LaunchedEffect` inside a loop or conditional that changes frequently
- Never launch coroutines in composition scope without `LaunchedEffect`
- Never read mutable state inside `DisposableEffect` without it being a key
- Prefer `rememberCoroutineScope()` for event-triggered coroutines (onClick, etc.)

---

## Navigation (2.8+)

### Type-Safe Routes with @Serializable

```kotlin
// Define routes
@Serializable object Home
@Serializable data class Detail(val id: String)
@Serializable data class Settings(val section: String? = null)

// NavHost
NavHost(navController, startDestination = Home) {
    composable<Home> {
        HomeScreen(onItemClick = { id -> navController.navigate(Detail(id)) })
    }
    composable<Detail> { backStackEntry ->
        val detail: Detail = backStackEntry.toRoute()
        DetailScreen(detail.id)
    }
    composable<Settings> { backStackEntry ->
        val settings: Settings = backStackEntry.toRoute()
        SettingsScreen(settings.section)
    }
}
```

### Navigation Rules

- Define routes as `@Serializable` objects/data classes (not string routes)
- Use `toRoute<T>()` extension to extract typed arguments
- Navigate with `navController.navigate(Route(...))` -- type-safe
- Single NavHost per navigation graph; nested graphs for feature modules

---

## Testing

### ComposeTestRule

```kotlin
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun showsTitle() {
    composeTestRule.setContent {
        MyScreen(title = "Hello")
    }
    composeTestRule.onNodeWithText("Hello").assertIsDisplayed()
}
```

### Semantic Matchers

```kotlin
composeTestRule.onNodeWithTag("submit_button").performClick()
composeTestRule.onNodeWithContentDescription("Close").assertExists()
composeTestRule.onAllNodesWithText("Item").assertCountEquals(3)
```

### testTag

```kotlin
// Production code
Button(
    onClick = { /* ... */ },
    modifier = Modifier.testTag("submit_button")
) { Text("Submit") }

// Test code
composeTestRule.onNodeWithTag("submit_button").performClick()
```

### Screenshot Testing

Use `screenshotRule` or Roborazzi for visual regression:

```kotlin
@get:Rule
val screenshotRule = createComposeRule()

@Test
fun screenshotHomeScreen() {
    screenshotRule.setContent {
        AppTheme { HomeScreen(fakeState) }
    }
    screenshotRule.onRoot().captureRoboImage("HomeScreen.png")
}
```
