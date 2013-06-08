package com.joshmoles.byobcontroller;

import android.os.Parcel;
import android.os.Parcelable;

public class PubnubParcelable implements Parcelable {
	 private int mData;
	
	 public int describeContents() {
	     return 0;
	 }
	
	 public void writeToParcel(Parcel out, int flags) {
	     out.writeInt(mData);
	 }
	
	 public static final Parcelable.Creator<PubnubParcelable> CREATOR 
	 	= new Parcelable.Creator<PubnubParcelable>() {
	     public PubnubParcelable createFromParcel(Parcel in) {
	         return new PubnubParcelable(in);
	     }
	
	     public PubnubParcelable[] newArray(int size) {
	         return new PubnubParcelable[size];
	     }
	 };
	
	 private PubnubParcelable(Parcel in) {
	     mData = in.readInt();
	 }
}