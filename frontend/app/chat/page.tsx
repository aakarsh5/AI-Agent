import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const page = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Chat Page</h1>
      <div className="flex w-full max-w-sm items-center gap-2">
        <Input type="text" placeholder="Click to chat" />
        <Button type="submit" variant="outline">
          Subscribe
        </Button>
      </div>
    </div>
  );
};

export default page;
