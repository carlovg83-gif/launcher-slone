# SLÖNE TV Launcher - ProGuard & R8 Optimization Rules

# Kotlin Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}

# AndroidX Compose & Lifecycle
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# Media3 ExoPlayer
-keep class androidx.media3.** { *; }
-dontwarn androidx.media3.**
-keepattributes *Annotation*,InnerClasses,Signature,EnclosingMethod

# Keep application entry points and activities
-keep class com.example.slnelauncher.** { *; }
-keepclassmembers class * extends android.app.Activity {
   public void *(android.view.View);
}
